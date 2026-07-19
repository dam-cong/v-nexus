import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.png', 'icons.svg', 'logo-mark.png', 'logo-full.png', 'fonts/*.woff2'],
      manifest: {
        name: 'V-NEXUS SCHOOL: AI-powered Adaptive Learning Platform',
        short_name: 'V-NEXUS SCHOOL',
        description: 'AI-powered Adaptive Learning Platform — học Tiếng Anh cá nhân hóa',
        theme_color: '#6C63FF',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          { src: '/favicon.png', sizes: '64x64', type: 'image/png' },
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
        // Ảnh minh hoạ trang landing (HS/PH/GV) nặng 2-4MB, không thuộc luồng luyện tập
        // offline cốt lõi -> loại khỏi precache thay vì nâng maximumFileSizeToCacheInBytes,
        // tránh service worker tải thêm ~9MB lúc cài đặt.
        globIgnores: ['**/assets/HS-*.png', '**/assets/PH-*.png', '**/assets/GV-*.png'],
        cleanupOutdatedCaches: true,
        navigateFallback: 'index.html',
        navigateFallbackDenylist: [/^\/api\//, /\.[a-z]{2,}$/i],
        navigateFallbackAllowlist: [/^\//],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: { cacheName: 'google-fonts-cache', expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 } }
          },
          {
            urlPattern: ({ url, request }) => url.pathname.startsWith('/api/')
              && request.method === 'GET'
              && !url.pathname.includes('/questions'),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: { maxEntries: 80, maxAgeSeconds: 60 * 60 * 24 },
              cacheableResponse: { statuses: [0, 200] }
            }
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
  },
  preview: {
    port: 8501,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.GATEWAY_URL || 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
