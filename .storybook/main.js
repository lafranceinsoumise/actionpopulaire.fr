const webpackConfig = require("../webpack.common");

module.exports = {
  stories: ["../agir/*/components/**/*.stories.js"],
  addons: ["@storybook/addon-links", "@storybook/addon-essentials"],
  webpackFinal: (config) => ({
    ...config,
    resolve: {
      ...config.resolve,
      alias: { ...config.resolve.alias, ...webpackConfig.resolve.alias },
    },
  }),
};
