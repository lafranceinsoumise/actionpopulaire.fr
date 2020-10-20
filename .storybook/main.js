const webpackConfig = require("../webpack.common");

module.exports = {
  stories: ["../agir/*/components/**/*.stories.js"],
  addons: ["@storybook/addon-links", "@storybook/addon-essentials"],
  webpackFinal: (config) => {
    config.module.rules.push({
      test: /\.scss$/,
      exclude: [/theme\/theme.scss/],
      use: ["style-loader", "css-loader", "sass-loader"],
    });

    config.resolve = {
      ...config.resolve,
      alias: { ...config.resolve.alias, ...webpackConfig.resolve.alias },
    };

    config.devtool = "eval";

    return config;
  },
};
