import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()], // plugin de react
  base: '/', // raiz; github pages del informe usa /docs, no este build
  server: {
    port: 5173, // puerto de vite en desarrollo
    host: true, // escucha en 0.0.0.0
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // solo si el backend corre en el host
        changeOrigin: true, // reescribe host
        rewrite: (path) => path.replace(/^\/api/, ''), // /api/auth/login -> /auth/login
      },
    },
  },
})
