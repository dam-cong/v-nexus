// V2-only dev/build configuration. The legacy Vite config remains untouched.
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 8501,
    host: '0.0.0.0',
    allowedHosts: ['v-nexus.editech.vn', '.ngrok-free.app', '.ngrok.app'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  }
})
