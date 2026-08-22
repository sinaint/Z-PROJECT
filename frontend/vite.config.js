import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // /api, /accounts로 가는 요청을 Django(127.0.0.1:8000)로 그대로 전달해요.
      // changeOrigin: true로 해야 Django의 ALLOWED_HOSTS 체크를 통과해요.
      // 브라우저 입장에선 계속 5173에만 접속하는 걸로 보여서, 세션 쿠키/CSRF도
      // 별도 설정(CORS 등) 없이 Django 템플릿에서 쓰던 것과 똑같이 동작해요.
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/accounts': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
