<template>
  <div class="intro">
    <h1 class="welcome">¡Bienvenido a la aplicación para analizar tu imagen con IA!</h1>

    <div class="slider">
      <button class="nav prev" :disabled="index===0" @click="prev">←</button>

      <div class="viewport" @keyup.right="next" @keyup.left="prev" tabindex="0">
        <Transition name="slide" mode="out-in">
          <section class="slide" :key="index">
            <div class="slide-content">
              <h2 class="title">{{ slides[index].title }}</h2>
              <p class="desc" v-if="slides[index].desc">{{ slides[index].desc }}</p>

              <img
                v-if="slides[index].img"
                :src="slides[index].img"
                alt=""
                class="sample"
                :class="slides[index].imgClass"
                />

            </div>
          </section>
        </Transition>
      </div>

      <button class="nav next" :disabled="index===slides.length-1" @click="next">→</button>
    </div>

    <div class="dots">
      <span v-for="(s, i) in slides" :key="i" class="dot" :class="{active: i===index}" @click="go(i)"></span>
    </div>

    <button v-if="index===slides.length-1" class="start" @click="$emit('start')">
      Empezar
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Rutas de ejemplo; pon una imagen en /public/sample-example.png
const slides = [
  {
    title: '1. Selecciona la imagen que quieres analizar',
    desc: 'Sube una imagen desde tu dispositivo.',
    img: '/select-from-computer.png',
    imgClass: 'small-img'
  },
  {
    title: '2. Selecciona el modelo que quieres aplicar',
    desc: 'Elige el servicio de IA en el desplegable para procesar tu imagen.',
    img: '/select-model-example.png',
    imgClass: ''
  },
  {
    title: '3. ¡Todo listo!',
    desc: 'Podrás visualizar la comparativa y descargar el resultado transformado.',
    img: null,
    imgClass: ''
  }
]

const index = ref(0)
const next = () => { if (index.value < slides.length - 1) index.value++ }
const prev = () => { if (index.value > 0) index.value-- }
const go   = (i) => { index.value = i }

onMounted(() => {
  // focus para que funcionen ← →
  const vp = document.querySelector('.viewport')
  vp && vp.focus()
})
</script>

<style scoped>
.intro {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
  color: #fff;
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  background: rgba(2, 8, 36, 0.40);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 1.5rem;
  backdrop-filter: blur(6px);
}

.welcome {
  font-size: 1.4rem;
  margin-bottom: 1rem;
}

.slider {
  display: grid;
  grid-template-columns: 48px 1fr 48px;
  gap: 0.5rem;
  align-items: center;
}

.viewport {
  min-height: 260px;
  outline: none;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.slide { width: 100%; }
.slide-content { padding: 0.5rem 0.75rem; }

.title { font-size: 1.25rem; margin-bottom: 0.5rem; }
.desc  { opacity: 0.9; margin-bottom: 0.75rem; }
.sample {
  max-width: min(100%, 640px);
  max-height: 280px;
  object-fit: contain;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.35);
}

.nav {
  height: 48px; width: 48px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.08);
  color: #fff;
  border-radius: 12px;
  cursor: pointer;
}
.nav:disabled { opacity: 0.35; cursor: not-allowed; }

.dots { margin-top: 0.75rem; }
.dot {
  display: inline-block; width: 10px; height: 10px;
  border-radius: 50%;
  background: rgba(255,255,255,0.35);
  margin: 0 6px; cursor: pointer;
}
.dot.active { background: #fff; }

.start {
  margin-top: 1rem;
  padding: 0.9rem 1.6rem;
  border: none; border-radius: 12px;
  background: #10b981; color: #fff;
  cursor: pointer; font-size: 1.05rem;
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

/* Animación izquierda→derecha */
.slide-enter-from { transform: translateX(40px); opacity: 0; }
.slide-leave-to   { transform: translateX(-40px); opacity: 0; }
.slide-enter-active, .slide-leave-active { transition: all .28s ease; }

.sample {
  max-width: min(100%, 640px);
  max-height: 280px;
  object-fit: contain;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.35);
  margin-top: 1rem;
}

.small-img {
  max-width: 200px;
  max-height: 200px;
}
</style>