import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: true,
    proxy: {
      // All /terminal/* calls → terminal-backend (no CORS, same-origin)
      '/terminal': {
        target: 'http://localhost:8085',
        changeOrigin: true,
        secure: false,
      },
      // Gateway API endpoints
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/auth': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth/, ''),
      },
      '/billing-api': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/billing-api/, ''),
      },
    }
  }
})
