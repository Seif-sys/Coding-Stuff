import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],   // keep whatever the template generated here
  server: {
    proxy: {
      '/health': 'http://localhost:8000',
      '/documents': 'http://localhost:8000',
      '/ask': 'http://localhost:8000', // also covers /ask/stream
    },
  },
})