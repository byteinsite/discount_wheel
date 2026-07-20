import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

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
});
