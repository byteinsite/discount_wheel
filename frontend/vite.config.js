import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/auth": "http://localhost:8000",
      "/me": "http://localhost:8000",
      "/spin": "http://localhost:8000",
      "/result": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },

  // Настройки для продакшена на Railway
  preview: {
    allowedHosts: [
      'discountwheel-copy-production.up.railway.app'
    ], // Это снимет блокировку host allowed
    host: true,
    port: process.env.PORT ? Number(process.env.PORT) : 4173,
    proxy: {
      "/auth": process.env.VITE_API_URL || "http://localhost:8000",
      "/me": process.env.VITE_API_URL || "http://localhost:8000",
      "/spin": process.env.VITE_API_URL || "http://localhost:8000",
      "/result": process.env.VITE_API_URL || "http://localhost:8000",
      "/health": process.env.VITE_API_URL || "http://localhost:8000",
    }
  }
})
