import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'icons.svg', 'fonts/*.woff2'],
      manifest: {
        name: 'V-Nexus Tutor',
        short_name: 'V-Nexus',
        description: 'Gia sư thích ứng — học Tiếng Anh cá nhân hóa',
        theme_color: '#6C63FF',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          { src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: { cacheName: 'google-fonts-cache', expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 } }
          }
        ]
      }
    })
  ],
  server: {
    port: 8501,
    host: '0.0.0.0',
    allowedHosts: ['v-nexus.editech.vn'],
    proxy: {
      '/api': {
        target: process.env.GATEWAY_URL || 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
