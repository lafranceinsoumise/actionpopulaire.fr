const path = require('path');
const merge = require('webpack-merge');
const webpack = require('webpack');

const common = require('./webpack.common.js');

module.exports = merge(common, {
  devtool: 'inline-source-map',
  output: {
    publicPath: 'http://localhost:3000/assets/components/',
    filename: '[name]-[hash].js',
  },
  devServer: {
    contentBase: path.join(__dirname, '/assets/components/'),
    compress: true,
    hot: true,
    hotOnly: true,
    port: 3000,
    headers: {
      'Access-Control-Allow-Origin': '*'
    }
  },
  plugins: [
    new webpack.NoEmitOnErrorsPlugin(),
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NamedModulesPlugin(),
  ],
});
