import dts from 'vite-plugin-dts';

export default {
  /*
  plugins: [
    dts({
      insertTypesEntry: true,
    }),
  ],
  */
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
