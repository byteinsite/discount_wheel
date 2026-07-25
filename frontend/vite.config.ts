import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

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
  preview: {
    allowedHosts: 'all', // Убирает ошибку "Blocked request"
    host: true,
    port: Number(process.env.PORT) || 4173, // Передаем порт от Railway
    proxy: {
      // Подставляем URL вашего FastAPI бэкенда на Railway
      "/auth": process.env.VITE_API_URL || "http://localhost:8000",
      "/me": process.env.VITE_API_URL || "http://localhost:8000",
      "/spin": process.env.VITE_API_URL || "http://localhost:8000",
      "/result": process.env.VITE_API_URL || "http://localhost:8000",
      "/health": process.env.VITE_API_URL || "http://localhost:8000",
    }
  }
});
