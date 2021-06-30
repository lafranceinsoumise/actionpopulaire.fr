const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const path = require("path");
const webpack = require("webpack");
const merge = require("webpack-merge");

const common = require("./webpack.common.js");
const { CONFIG_TYPES } = require("./webpack.common");

const STATIC_URL = "/static";

module.exports = merge.merge(common, {
  devtool: "source-map",
  output: {
    publicPath: path.join(STATIC_URL, "components/"),
    assetModuleFilename: "files/[hash][ext][query]",
    devtoolModuleFilenameTemplate: "webpack://[absolute-resource-path]",
  },
  mode: "production",
  plugins: [
    new webpack.EnvironmentPlugin({
      SENTRY_RELEASE: require("child_process")
        .execSync("git rev-parse HEAD")
        .toString()
        .replace("\n", ""),
      SENTRY_ENV: "production",
    }),
  ],
});
