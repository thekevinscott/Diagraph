module.exports = {
  presets: [require.resolve('@docusaurus/core/lib/babel/preset')],
  plugins: [
    ["@babel/plugin-proposal-decorators", { "version": "2023-05" }],
    // ["@babel/plugin-proposal-class-properties", { "loose": true }]
    ["@babel/transform-class-properties", { "loose": true }],
    ["@babel/plugin-transform-class-static-block",],

  ],

};
