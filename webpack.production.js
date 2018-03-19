const webpack = require('webpack');
const merge = require('webpack-merge');
const UglifyJSWebpackPlugin = require('uglifyjs-webpack-plugin');

const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'production',
  plugins: [
    new webpack.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify('production')
    })
  ]
});
