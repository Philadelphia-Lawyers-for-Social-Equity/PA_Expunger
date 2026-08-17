import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';

export default defineConfig(() => {
  return {
    plugins: [react()],
    server: {port: 3000},
    test:{
      environment: 'jsdom',
      setupFiles: "./src/setupTests.js",
      clearMocks: true,
    }
  };
});
