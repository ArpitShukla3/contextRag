import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const BACKEND_TARGET = 'http://localhost:8000'

const proxy = {
  '/api': {
    target: BACKEND_TARGET,
    changeOrigin: true,
  },
}

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy,
  },
  preview: {
    proxy,
  },
})