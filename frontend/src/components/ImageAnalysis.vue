<template>
  <div class="container">
    <h2>Analizar imagen con IA</h2>

    <!-- Grupo: modelo -->
    <div class="form-group">
      <label class="form-label">Selecciona un modelo:</label>
      <select v-model="selectedModel" class="input-select">
        <option disabled value="">Selecciona un modelo</option>
        <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
      </select>
    </div>

    <!-- Grupo: archivo -->
    <div class="form-group">
      <label class="form-label">Selecciona una imagen:</label>

      <label class="file-btn">
        <input type="file" accept="image/*" @change="onFileChange" />
        <span class="file-btn-text">Elegir archivo</span>
      </label>

      <span v-if="selectedFileName" class="file-name">{{ selectedFileName }}</span>
    </div>

    <!-- Botón de análisis -->
    <button class="btn-primary" :disabled="!canSubmit || loading" @click="analyzeImage">
      {{ loading ? 'Procesando...' : 'Comenzar' }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- Resultados -->
    <div class="results-area">
      <div v-if="resultUrl" class="compare">
        <!-- ORIGINAL: se expande si es horizontal -->
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

const models = ['Modelo A', 'Modelo B', 'Modelo C'] // ajusta a tus servicios reales
const selectedModel = ref('')
const selectedFile = ref(null)
const selectedFileName = ref('')
const originalPreviewUrl = ref(null)
const resultUrl = ref(null)
const isHorizontal = ref(false)   // <-- detecta si la imagen original es apaisada
const loading = ref(false)
const error = ref('')

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

  // Preview de original
  revoke(originalPreviewUrl.value)
  originalPreviewUrl.value = URL.createObjectURL(file)

  // Detecta orientación (horizontal vs vertical)
  const img = new Image()
  img.onload = () => {
    isHorizontal.value = img.width > img.height
  }
  img.src = originalPreviewUrl.value

  // Reset de resultado si se cambia la imagen
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
  formData.append('service_name', selectedModel.value) // backend espera este nombre
  formData.append('image_file', selectedFile.value)    // backend espera este nombre

  const token = await getIdToken()

  return axios.post(`${API_BASE}${ANALYSIS_PATH}`, formData, {
    headers: { Authorization: `Bearer ${token}` },
    responseType: 'blob',
  })
}

const analyzeImage = async () => {
  error.value = ''
  if (!canSubmit.value) return
  loading.value = true

  try {
    const response = await postAnalysis()
    const mime = response.headers?.['content-type'] || 'image/png'
    revoke(resultUrl.value)
    resultUrl.value = URL.createObjectURL(new Blob([response.data], { type: mime }))
  } catch (err) {
    const status = err?.response?.status
    if (status === 401 || status === 403) {
      try {
        idToken = null
        await getIdToken()
        const response = await postAnalysis()
        const mime = response.headers?.['content-type'] || 'image/png'
        revoke(resultUrl.value)
        resultUrl.value = URL.createObjectURL(new Blob([response.data], { type: mime }))
      } catch (err2) {
        console.error('Error en análisis (reintento):', err2)
        error.value = 'No se pudo completar el análisis tras renovar el token.'
      }
    } else {
      console.error('Error en análisis:', err)
      error.value = 'Hubo un error al analizar la imagen.'
    }
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  revoke(originalPreviewUrl.value)
  revoke(resultUrl.value)
})
</script>

<style scoped>
/* Arial en negrita en todo el componente */
:host, .container, .container * {
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
}

/* Panel general, ahora más ANCHO para favorecer horizontales */
.container {
  width: 100%;
  max-width: 1400px;         /* <<< más ancho del panel */
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

/* Formulario con separación cómoda */
.form-group { margin: 1.25rem 0 1.6rem; }
.form-label { display: block; margin-bottom: 0.6rem; }

/* SELECT oscuro y legible */
.input-select {
  appearance: none;
  width: 100%;
  padding: 0.9rem 1rem;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.25);
  background-color: rgba(15,32,60,0.85);
  color: #fff;
  outline: none;
  background-image: linear-gradient(45deg, transparent 50%, #ffffff 50%),
                    linear-gradient(135deg, #ffffff 50%, transparent 50%),
                    linear-gradient(to right, transparent, transparent);
  background-position: calc(100% - 20px) calc(50% - 4px),
                       calc(100% - 15px) calc(50% - 4px),
                       calc(100% - 2.5rem) 0.6rem;
  background-size: 5px 5px, 5px 5px, 1px 1.6rem;
  background-repeat: no-repeat;
}
.input-select:focus {
  border-color: rgba(255,255,255,0.55);
  box-shadow: 0 0 0 3px rgba(255,255,255,0.15);
}
.input-select option { background: #020824; color: #fff; }

/* Botón de archivo visual */
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
  transition: background .2s ease, transform .05s ease;
  user-select: none;
}
.file-btn:hover { background: #0284c7; }
.file-btn:active { transform: translateY(1px); }
.file-btn input[type="file"] { display: none; }
.file-btn-text { pointer-events: none; }

.file-name {
  display: inline-block;
  margin-left: 0.75rem;
  opacity: 0.9;
  word-break: break-all;
}

/* Botones principales */
.btn-primary, .btn-secondary {
  display: inline-block;
  padding: 1rem 1.7rem;
  font-size: 1.05rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  margin-top: 1.1rem;
  transition: transform .05s ease, box-shadow .2s ease, background .2s ease;
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}
.btn-primary { background-color: #2563eb; color: #fff; }
.btn-primary:hover:enabled { background-color: #1d4ed8; }
.btn-primary:active:enabled { transform: translateY(1px); }

.btn-secondary { background-color: #10b981; color: #fff; margin-top: 0.9rem; }
.btn-secondary:hover:enabled { background-color: #059669; }
.btn-secondary:active:enabled { transform: translateY(1px); }

button:disabled { background-color: #6b7280; cursor: not-allowed; box-shadow: none; }

.error { margin-top: 1rem; color: #ffd2d2; }

/* Resultados con altura reservada para evitar saltos */
.results-area { margin-top: 1.5rem; min-height: 480px; }

/* Grid comparativa: 2 columnas por defecto */
.compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  align-items: start;
}

/* Placeholder invisible con mismo tamaño para evitar rebotes */
.placeholder-block .card { min-height: 360px; opacity: 0; }

/* Tarjetas */
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
.card-title { margin: 0 0 0.75rem 0; font-size: 1.15rem; }
.card-body { display: flex; flex-direction: column; align-items: center; }

/* Imagenes: más grandes; horizontales aprovecharán más ancho con wide-card */
.img {
  max-width: 100%;
  max-height: 420px;         /* más alto para que horizontales se vean grandes */
  object-fit: contain;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.3);
}

/* Cuando la original es horizontal, expandimos la tarjeta a 2 columnas */
.wide-card { grid-column: span 2; }
.wide-card .img { max-height: 520px; }  /* permite aún más altura en horizontales */
.compare .wide-card + .card { margin-top: 1rem; }

/* Responsive */
@media (max-width: 1200px) {
  .container { max-width: 96vw; }
  .img { max-height: 380px; }
  .wide-card .img { max-height: 460px; }
}
@media (max-width: 900px) {
  .results-area { min-height: 540px; }
  .compare { grid-template-columns: 1fr; }
  .wide-card { grid-column: span 1; } /* en móvil vuelve a una columna */
  .img { max-height: 360px; }
}
</style>