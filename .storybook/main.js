const webpackConfig = require("../webpack.common");
const baseConfig = webpackConfig(webpackConfig.CONFIG_TYPES.DEV);

module.exports = {
  stories: ["../agir/*/components/**/*.stories.js"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-webpack5-compiler-babel",
    "storybook-dark-mode",
  ],
  staticDirs: ["../.storybook/public"],
  webpackFinal: (config) => {
    config.module.rules.push({
      test: /\.scss$/,
      exclude: [/theme\/theme.scss/],
      use: [
        "style-loader",
        {
          loader: "css-loader",
          options: {
            modules: {
              mode: "icss",
              auto: /\.scss$/i,
            },
          },
        },
        "sass-loader",
      ],
    });
    config.resolve = {
      ...config.resolve,
      alias: {
        ...config.resolve.alias,
        ...baseConfig.resolve.alias,
      },
    };
    config.devtool = "eval";
    config.watchOptions = {
      ...config.watchOptions,
      ignored: ["/theme.scss$/", "**/node_modules"],
    };
    return config;
  },
  framework: {
    name: "@storybook/react-webpack5",
    options: {},
  },
  docs: {
    autodocs: true,
  },
};
