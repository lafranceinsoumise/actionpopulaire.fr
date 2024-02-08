const merge = require("webpack-merge");
const common = require("./webpack.common");

const production = {
  mode: "production",
  devtool: "source-map",
  output: {
    publicPath: "/",
    devtoolModuleFilenameTemplate: "webpack://[absolute-resource-path]",
  },
  devServer: {
    hot: false,
    inline: false,
    liveReload: false,
  },
};

const es5Config = merge.merge(common(common.CONFIG_TYPES.ES5), production);
const es2015Config = merge.merge(
  common(common.CONFIG_TYPES.ES2015),
  production,
);

module.exports = [es5Config, es2015Config];
