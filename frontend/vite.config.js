import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: './',          // necesario para S3
  plugins: [vue()],
})