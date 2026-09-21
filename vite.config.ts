import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { edgeTtsMiddleware } from './plugins/edge-tts-middleware.ts'

export default defineConfig({
  base: '/vox-lux/',
  plugins: [react(), tailwindcss(), edgeTtsMiddleware()],
})
