const path = require("path");
const merge = require("webpack-merge");
const ReactRefreshWebpackPlugin = require("@pmmmwh/react-refresh-webpack-plugin");

const common = require("./webpack.common.js");

const serverName = process.env.JS_SERVER || "agir.local";
const port = process.env.JS_SERVER
  ? +process.env.JS_SERVER.split(":")[1] || 3000
  : 3000;

module.exports = merge.merge(common("dev"), {
  mode: "development",
  devtool: "eval-cheap-module-source-map",
  output: {
    publicPath: `http://${serverName}:${port}/static/components/`,
    devtoolModuleFilenameTemplate: "webpack://[absolute-resource-path]",
    filename: "[name].js",
    pathinfo: false,
  },
  optimization: {
    removeAvailableModules: false,
    removeEmptyChunks: false,
    splitChunks: false,
    moduleIds: "named",
    chunkIds: "named",
    emitOnErrors: false,
  },
  watchOptions: {
    poll: 1000,
    ignored: /theme\.scss$/,
  },
  devServer: {
    hot: "only",
    host: serverName === "localhost" ? "localhost" : "0.0.0.0",
    port: port,
    devMiddleware: {
      publicPath: `http://${serverName}:${port}/static/components/`,
      writeToDisk: true,
    },
    client: {
      webSocketURL: `auto://${serverName}:${port}`,
    },
    static: {
      directory: path.join(__dirname, "/assets/components/"),
      watch: false,
    },
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
    allowedHosts: ["agir.local"],
  },
  plugins: [new ReactRefreshWebpackPlugin()],
});
