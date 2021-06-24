const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const path = require("path");
const webpack = require("webpack");
const merge = require("webpack-merge");

const common = require("./webpack.common.js");

const STATIC_URL = "/static";

const production = {
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
};

const createCompiler = (config) => {
  const compiler = webpack(config);
  return () => {
    return new Promise((resolve, reject) => {
      compiler.run((err, stats) => {
        if (err) return reject(err);
        console.log(stats.toString({ colors: true }) + "\n");
        resolve();
      });
    });
  };
};

const legacyConfig = merge.merge(
  {
    plugins: [new CleanWebpackPlugin()],
  },
  common("es5"),
  production
);
const modernConfig = merge.merge(common("es2015+"), production);

(async () => {
  await createCompiler(legacyConfig)();
  await createCompiler(modernConfig)();
})();
