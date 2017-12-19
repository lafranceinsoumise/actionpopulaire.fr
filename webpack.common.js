const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker')


const DISTPATH = path.resolve(__dirname, 'src/assets/components');

module.exports = {
  context: path.resolve(__dirname, 'src/javascript_components'),
  entry: {
    richEditor: './richEditor.js',
    helpDialog: './helpDialog.js'
  },
  plugins: [
    new CleanWebpackPlugin([DISTPATH]),
    new BundleTracker({path: DISTPATH}),
  ],
  output: {
    libraryTarget: 'window',
    library: '[name]',
    filename: '[name]-[chunkhash].js',
    path: DISTPATH
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader?cacheDirectory=true',
          options: {
            presets: ['babel-preset-env', 'babel-preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        exclude: /node_modules\/tinymce/,
        use: [
          {loader: 'style-loader'},
          {loader: 'css-loader'}
        ]
      }
    ]
  },
  target: 'web'
};
