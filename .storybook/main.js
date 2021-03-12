const webpackConfig = require("../webpack.common");

module.exports = {
  core: {
    builder: "webpack5",
  },
  stories: ["../agir/*/components/**/*.stories.js"],
  addons: ["@storybook/addon-links", "@storybook/addon-essentials"],
  webpackFinal: (config) => {
    config.module.rules.push({
      test: /\.scss$/,
      exclude: [/theme\/theme.scss/],
      use: [
        "style-loader",
        {
          loader: "css-loader",
          options: {
            modules: { compileType: "icss", auto: /\.scss$/i },
          },
        },
        "sass-loader",
      ],
    });

    config.resolve = {
      ...config.resolve,
      alias: { ...config.resolve.alias, ...webpackConfig.resolve.alias },
    };

    config.devtool = "eval";

    return config;
  },
};
