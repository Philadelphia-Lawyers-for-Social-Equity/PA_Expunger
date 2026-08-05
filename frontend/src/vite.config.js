import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';

export default defineConfig(({ command }) => {
  const config = {
    plugins: [react()],
    base: '/',
    server: {port: 3000},
    test:{
      environment: 'jsdom',
      setupFiles: "./src/setupTests.js",
      clearMocks: true,
    }
  };
  if (command === 'build') {
    // Django serves the built assets under STATIC_URL; see Dockerfile.prod.
    config.base = process.env.STATIC_URL || '/static/';
  }
  return config;
});
