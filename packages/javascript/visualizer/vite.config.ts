import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  define: {
    'process.env': {}
  },
  plugins: [react()],
  build: {
    target: 'esnext',
    minify: false,
    lib: {
      entry: './src/index.tsx',
      name: 'renderDiagraphVisualization',
      fileName: 'diagraph-visualizer',
      // format: 'umd',
    },
    rollupOptions: {
      // external: ['react', 'react-dom'],

      // input: './src/index.tsx',
      output: {
        // dir: 'dist',
        format: 'umd',
        // globals: {
        //   'react': 'React',
        //   'react-dom': 'ReactDOM',
        // },
        // entryFileNames: 'diagraph-visualizer.js',
      },
    },
  }
})
