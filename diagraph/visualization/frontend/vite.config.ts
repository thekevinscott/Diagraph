export default {
  build: {
    minify: false,
    rollupOptions: {
      input: './src/index.ts',
      output: {
        dir: 'dist',
        format: 'es',
        entryFileNames: 'diagraph.js',
      },
    },
  }
};
