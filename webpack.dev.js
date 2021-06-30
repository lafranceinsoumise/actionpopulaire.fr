const path = require("path");
const merge = require("webpack-merge");
const webpack = require("webpack");
const ReactRefreshWebpackPlugin = require("@pmmmwh/react-refresh-webpack-plugin");

const common = require("./webpack.common.js");

common.module.rules[0].use.options.plugins = [
  require.resolve("react-refresh/babel"),
];

const serverName = process.env.JS_SERVER || "agir.local";
const port = process.env.JS_SERVER
  ? +process.env.JS_SERVER.split(":")[1] || 3000
  : 3000;

module.exports = merge.merge(common, {
  mode: "development",
  devtool: "eval-source-map",
  output: {
    publicPath: `http://${serverName}:${port}/static/components/`,
    devtoolModuleFilenameTemplate: "webpack://[absolute-resource-path]",
    filename: "[name]-[fullhash].js",
  },
  watchOptions: {
    poll: 1000,
  },
  devServer: {
    publicPath: `http://${serverName}:${port}/static/components/`,
    public: `${serverName}:${port}`,
    contentBase: path.join(__dirname, "/assets/components/"),
    compress: true,
    hot: true,
    hotOnly: true,
    host: serverName === "localhost" ? "localhost" : "0.0.0.0",
    port: port,
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
    writeToDisk: true,
    allowedHosts: ["agir.local"], // l'appli Django est toujours sur agir.local
    injectClient: ({ name }) => name !== "chill",
    injectHot: ({ name }) => name !== "chill",
  },
  optimization: {
    moduleIds: "named",
    chunkIds: "named",
    emitOnErrors: false,
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    new ReactRefreshWebpackPlugin(),
    new webpack.EnvironmentPlugin({
      DEBUG: "agir:*", // default value if not defined in .env
    }),
  ],
});
