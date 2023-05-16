import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import createPlugin from 'vite-plugin-raw';
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), createPlugin({match: /\.txt$/})],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
})
