<template>
  <div class="container">
    <h2>Analizar imagen con IA</h2>

    <!-- Grupo: modelo -->
    <div class="form-group">
      <label class="form-label">Selecciona un modelo:</label>
      <select v-model="selectedModel" class="input-select">
        <option disabled value="">Selecciona un modelo</option>
        <option v-for="m in models" :key="m.id" :value="m.id">
          {{ m.label }}
        </option>
      </select>

      <!-- Descripción + ejemplo -->
      <div v-if="selectedModel" class="model-info">
        <p>{{ models.find(m => m.id === selectedModel)?.desc }}</p>
        <img
          v-if="models.find(m => m.id === selectedModel)?.example"
          :src="models.find(m => m.id === selectedModel)?.example"
          alt="Ejemplo del modelo"
          class="example-img"
        />
      </div>
    </div>

    <!-- Grupo: archivo -->
    <div class="form-group">
      <label class="form-label">Selecciona una imagen:</label>

      <label class="file-btn">
        <input type="file" accept="image/*" @change="onFileChange" />
        <span class="file-btn-text">Elegir archivo</span>
      </label>

      <span v-if="selectedFileName" class="file-name">{{ selectedFileName }}</span>

      <!-- 👇 Previsualización de la imagen original -->
      <div v-if="originalPreviewUrl" class="preview-block">
        <h3 class="card-title">Vista previa</h3>
        <img :src="originalPreviewUrl" alt="Vista previa de la imagen" class="preview-img" />
      </div>
    </div>

    <!-- Botón de análisis -->
    <button class="btn-primary" :disabled="!canSubmit || loading" @click="analyzeImage">
      {{ loading ? 'Procesando...' : 'Comenzar' }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- Spinner de espera -->
    <div v-if="waitingResult" class="spinner">
      <div class="loader"></div>
      <p>Procesando tu imagen, por favor espera...</p>
    </div>

    <!-- Resultados -->
    <div class="results-area">
      <div v-if="resultUrl" class="compare">
        <!-- ORIGINAL -->
        <div class="card" :class="{ 'wide-card': isHorizontal }">
          <h3 class="card-title">Original</h3>
          <div class="card-body">
            <img v-if="originalPreviewUrl" :src="originalPreviewUrl" alt="Imagen original" class="img" />
          </div>
        </div>

        <!-- TRANSFORMADA -->
        <div class="card">
          <h3 class="card-title">Transformada</h3>
          <div class="card-body">
            <img :src="resultUrl" alt="Imagen transformada" class="img" />
            <a :href="resultUrl" download="resultado.png">
              <button class="btn-secondary">Descargar imagen</button>
            </a>
          </div>
        </div>
      </div>

      <!-- Placeholder para reservar altura antes del resultado -->
      <div v-else class="compare placeholder-block" aria-hidden="true">
        <div class="card"></div>
        <div class="card"></div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import axios from 'axios'

const models = [
  {
    id: 'upscaling-ai',
    label: 'Upscaling Model',
    desc: 'Aumenta la resolución de la imagen preservando el detalle.',
    example: '' // /examples/upscaling.png
  },
  {
    id: 'denoising-ai',
    label: 'Denoising Model',
    desc: 'Elimina el ruido de la imagen para obtener un resultado más limpio.',
    example: '' // /examples/denoising.png
  },
  {
    id: 'inpainting-ai',
    label: 'Inpainting Model',
    desc: 'Rellena o reconstruye partes de la imagen donde aparece un texto.',
    example: '' // /examples/inpainting.png
  }
]

const selectedModel = ref('')
const selectedFile = ref(null)
const selectedFileName = ref('')
const originalPreviewUrl = ref(null)
const resultUrl = ref(null)
const isHorizontal = ref(false)
const loading = ref(false)
const error = ref('')
const waitingResult = ref(false)

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://ts5qfbdl7j.execute-api.eu-west-1.amazonaws.com/v1'
const AUTHORIZE_PATH = import.meta.env.VITE_AUTHORIZE_PATH || '/authorize/'
const ANALYSIS_PATH  = import.meta.env.VITE_ANALYSIS_PATH  || '/image-ai-analysis'

let idToken = null
let authorizing = false

const canSubmit = computed(() => !!selectedModel.value && !!selectedFile.value)

const revoke = (url) => { try { url && URL.revokeObjectURL(url) } catch {} }

const onFileChange = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  selectedFile.value = file
  selectedFileName.value = file.name

  revoke(originalPreviewUrl.value)
  originalPreviewUrl.value = URL.createObjectURL(file)

  const img = new Image()
  img.onload = () => {
    isHorizontal.value = img.width > img.height
  }
  img.src = originalPreviewUrl.value

  if (resultUrl.value) {
    revoke(resultUrl.value)
    resultUrl.value = null
  }
}

async function getIdToken () {
  if (idToken) return idToken
  if (authorizing) {
    await new Promise(resolve => {
      const poll = () => { if (!authorizing) return resolve(); setTimeout(poll, 50) }
      poll()
    })
    return idToken
  }
  try {
    authorizing = true
    const res = await axios.get(`${API_BASE}${AUTHORIZE_PATH}`)
    idToken = res?.data?.id_token
    if (!idToken) throw new Error('id_token no presente en la respuesta de /authorize/')
    return idToken
  } finally {
    authorizing = false
  }
}

async function postAnalysis () {
  const formData = new FormData()
  formData.append('service_name', selectedModel.value)
  formData.append('image_file', selectedFile.value)

  const token = await getIdToken()

  return axios.post(`${API_BASE}${ANALYSIS_PATH}`, formData, {
    headers: { Authorization: `Bearer ${token}` },
    responseType: 'json',
  })
}

const analyzeImage = async () => {
  error.value = ''
  if (!canSubmit.value) return
  loading.value = true
  waitingResult.value = false

  try {
    const response = await postAnalysis()
    const { success, image_id } = response.data

    if (success && image_id) {
      waitingResult.value = true
      startPolling(selectedModel.value, image_id)
    } else {
      throw new Error('Respuesta inesperada del backend')
    }
  } catch (err) {
    console.error('Error en análisis:', err)
    error.value = 'Hubo un error al iniciar el análisis.'
    loading.value = false
    waitingResult.value = false
  }
}

let pollInterval = null

function startPolling(serviceName, imageId) {
  if (pollInterval) clearInterval(pollInterval)

  let attempts = 0
  pollInterval = setInterval(async () => {
    attempts++
    if (attempts > 60) { // 60 intentos = 5 minutos
      clearInterval(pollInterval)
      pollInterval = null
      loading.value = false
      waitingResult.value = false
      error.value = 'El procesamiento ha tardado demasiado. Intenta de nuevo.'
      return
    }

    try {
      const token = await getIdToken()
      const res = await axios.get(`${API_BASE}/images/${serviceName}/${imageId}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      })

      if (res.status === 200 && res.data) {
        const mime = res.headers?.['content-type'] || 'image/png'
        revoke(resultUrl.value)
        resultUrl.value = URL.createObjectURL(new Blob([res.data], { type: mime }))

        clearInterval(pollInterval)
        pollInterval = null
        loading.value = false
        waitingResult.value = false
      }
    } catch (err) {
      console.log(`Intento ${attempts}: imagen aún no lista...`)
    }
  }, 5000)
}

onBeforeUnmount(() => {
  revoke(originalPreviewUrl.value)
  revoke(resultUrl.value)
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
:host, .container, .container * {
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
}

.container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
  background: rgba(11, 29, 58, 0.50);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  backdrop-filter: blur(8px) saturate(120%);
  color: #fff;
  min-height: 78vh;
}

.form-group { margin: 1.25rem 0 1.6rem; }
.form-label { display: block; margin-bottom: 0.6rem; }

.input-select {
  appearance: none;
  width: 100%;
  padding: 0.9rem 1rem;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.25);
  background-color: rgba(15,32,60,0.85);
  color: #fff;
  outline: none;
}
.input-select option { background: #020824; color: #fff; }

.file-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.95rem 1.25rem;
  border-radius: 12px;
  background: #0ea5e9;
  color: #00111f;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}
.file-btn input[type="file"] { display: none; }
.file-btn-text { pointer-events: none; }

.btn-primary, .btn-secondary {
  display: inline-block;
  padding: 1rem 1.7rem;
  font-size: 1.05rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  margin-top: 1.1rem;
}
.btn-primary { background-color: #2563eb; color: #fff; }
.btn-secondary { background-color: #10b981; color: #fff; margin-top: 0.9rem; }

.error { margin-top: 1rem; color: #ffd2d2; }

.results-area { margin-top: 1.5rem; min-height: 480px; }
.compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  align-items: start;
}
.card {
  background: rgba(0,0,0,0.25);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 14px;
  padding: 1rem;
  text-align: center;
  min-height: 360px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.img {
  max-width: 100%;
  max-height: 420px;
  object-fit: contain;
  border-radius: 10px;
}

.model-info {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  text-align: center;
}
.model-info p { margin-bottom: 0.75rem; font-size: 0.95rem; color: #e5e7eb; }

.preview-block { margin-top: 1rem; text-align: center; }
.preview-img {
  max-width: 320px;
  max-height: 220px;
  border-radius: 10px;
}

.spinner { margin-top: 1.5rem; text-align: center; }
.loader {
  border: 6px solid rgba(255,255,255,0.2);
  border-top: 6px solid #0ea5e9;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem auto;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
