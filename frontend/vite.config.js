import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      '/validate-json': 'http://localhost:8000',
      '/extract-and-validate-pdfs': 'http://localhost:8000',
      '/health': 'http://localhost:8000'
    }
  }
})
