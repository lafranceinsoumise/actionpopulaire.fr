const path = require("path");
const webpack = require("webpack");
const merge = require("webpack-merge");

const common = require("./webpack.common.js");

const STATIC_URL = "/static";

module.exports = merge.merge(common, {
  output: {
    publicPath: path.join(STATIC_URL, "components/"),
    assetModuleFilename: "files/[hash][ext][query]",
  },
  mode: "production",
  plugins: [
    new webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify("production"),
    }),
  ],
});
