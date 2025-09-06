<template>
  <main class="hero">
    <section class="content">
      <IntroSlides v-if="showIntro" @start="showIntro=false" />
      <ImageAnalysis v-else />
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import IntroSlides from './components/IntroSlides.vue'
import ImageAnalysis from './components/ImageAnalysis.vue'

const showIntro = ref(true)
</script>

<style>
:root { --bg-blue: #020824; }

html, body, #app, * { font-family: Arial, Helvetica, sans-serif; font-weight: 700; }

.hero {
  position: relative;
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  background:
    var(--bg-blue)
    url('/ai-bg.jpg') left center / clamp(45%, 55%, 60%) auto no-repeat;
  padding: 2rem 6rem 2rem 2rem;
  box-sizing: border-box;
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(
    to right,
    rgba(2, 8, 36, 0.65) 30%,
    rgba(2, 8, 36, 0.35) 55%,
    rgba(2, 8, 36, 0.00) 75%
  );
  pointer-events: none;
}
.content {
  position: relative; z-index: 1;
  max-width: 1100px;
  width: 100%;
  margin-right: 6%;
}

@media (max-width: 1024px) {
  .hero {
    padding: 1.25rem;
    background-position: center top;
    background-size: 90% auto;
  }
  .content { margin-right: 0; }
}

html, body, #app {
  height: 100%;
  background: #020824; 
  margin: 0;             
  padding: 0;
}

body { overflow-x: hidden; }

.hero { min-height: 100vh; width: 100vw; }

</style>