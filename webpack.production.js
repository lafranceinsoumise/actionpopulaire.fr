const path = require("path");
const webpack = require("webpack");
const merge = require("webpack-merge");

const common = require("./webpack.common.js");

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
    new webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify("production"),
      SENTRY_RELEASE: JSON.stringify(
        require("child_process")
          .execSync("git rev-parse HEAD")
          .toString()
          .replace("\n", "")
      ),
    }),
  ],
});
