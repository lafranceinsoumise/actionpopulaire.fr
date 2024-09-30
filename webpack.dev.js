const path = require("path");
const merge = require("webpack-merge");
const ReactRefreshWebpackPlugin = require("@pmmmwh/react-refresh-webpack-plugin");
const common = require("./webpack.common.js");

require("dotenv").config({
  path: path.join(__dirname, ".env"),
});

// Exemples de config :
//
// WEBPACK_SERVER_HOST : localhost:5000
// WEBPACK_SERVER_PORT : aucun
// Le serveur écoute sur le port 5000 et les liens générés pour les bundles utilisent localhost:5000
//
// WEBPACK_SERVER_HOST : agir.local
// WEBPACK_SERVER_PORT : 4000
// Le serveur écoute sur le port 4000 et les liens générés pour les bundles utilisent agir.local (sans numéro de port)
const serverName = process.env.WEBPACK_SERVER_HOST || "agir.local:3000";
const port = +process.env.WEBPACK_SERVER_PORT || +serverName.split(":")[1];

module.exports = merge.merge(common("dev"), {
  mode: "development",
  devtool: "eval-cheap-module-source-map",
  output: {
    publicPath: `http://${serverName}:${8000}/`,
    devtoolModuleFilenameTemplate: "webpack://[absolute-resource-path]",
    filename: "[name].js",
    pathinfo: false,
  },
  optimization: {
    removeAvailableModules: false,
    removeEmptyChunks: false,
    runtimeChunk: "single",
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
      publicPath: `http://${serverName}/`,
      writeToDisk: true,
    },
    client: {
      webSocketURL: `auto://${serverName}`,
    },
    static: {
      directory: path.join(__dirname, "/assets/"),
      watch: false,
    },
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
    allowedHosts: process.env.ALLOWED_HOSTS
      ? process.env.ALLOWED_HOSTS.split(",").map((host) => host.trim())
      : ["agir.local", ".ap.lfi.site"],
  },
  plugins: [new ReactRefreshWebpackPlugin()],
});
