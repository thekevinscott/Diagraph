import { resolve } from 'path';
import { defineConfig } from 'vite'
import { fileURLToPath } from 'url';
const __dirname = fileURLToPath(import.meta.url);

export default defineConfig({
  build: {
    outDir: resolve(__dirname, 'dist'),
    // rollupOptions: {
    //   input: {
    //     index: resolve(__dirname, './src/site/index.html'),
    //     docs: resolve(__dirname, './src/site/docs/index.html'),
    //   },
    // },
  },
  root: "./src",
    assetsInclude: ['**/*.md'],

  server: {
  //   open: 'index.html',
      headers: {
          "Cross-Origin-Embedder-Policy": "require-corp",
          "Cross-Origin-Opener-Policy": "same-origin",
      }
  },
});
