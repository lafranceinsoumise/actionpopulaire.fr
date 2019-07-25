const path = require("path");
const webpack = require("webpack");
const merge = require("webpack-merge");

const common = require("./webpack.common.js");

const STATIC_URL = "/static";

common.module.rules.find(
  r => r.loader === "file-loader"
).options.publicPath = path.join(STATIC_URL, "components", "files");

module.exports = merge(common, {
  mode: "production",
  plugins: [
    new webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify("production")
    })
  ],
  optimization: { splitChunks: { chunks: "all" } }
});
