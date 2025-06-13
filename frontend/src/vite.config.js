import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';

export default defineConfig(({ command }) => {
  const config = {
    plugins: [react()],
    base: '/',
    server: {port: 3000},
  };
  if (command === 'build') {
    config.base = '/static/';
  }
  return config;
});
