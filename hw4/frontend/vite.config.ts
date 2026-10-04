import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy API and image requests to the FastAPI backend so the browser sees one origin
// and catalogue image paths ("/media/products/x.jpg") work unchanged.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target: 'http://127.0.0.1:8001', changeOrigin: true },
      '/media': { target: 'http://127.0.0.1:8001', changeOrigin: true },
    },
  },
})
