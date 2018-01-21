const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const webpack = require('webpack');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const DISTPATH = path.resolve(__dirname, 'src/assets/components');
const cssName = require('@fi/theme/dist/assets.json')['main.css'];
const apiEndpoint = JSON.stringify(process.env.API_ENDPOINT || 'http://localhost:8000/legacy');


module.exports = {
  context: path.resolve(__dirname, 'src/javascript_components'),
  entry: {
    richEditor: './richEditor.js',
    helpDialog: './helpDialog.js',
    locationSearchField: './locationSearchField.js',
    createGroupForm: './createGroupForm',
    theme: '@fi/theme/dist/styles/' + cssName,
  },
  plugins: [
    new CleanWebpackPlugin([DISTPATH]),
    new BundleTracker({path: DISTPATH}),
    new ExtractTextPlugin('theme-[contenthash].css'),
    new webpack.DefinePlugin({'API_ENDPOINT': apiEndpoint}),
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
            presets: ['babel-preset-env', 'babel-preset-react'],
            plugins: ['react-hot-loader/babel']
          }
        }
      },
      {
        test: new RegExp('@fi/theme/dist/styles/' + cssName),
        use: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: 'css-loader'
        })
      },
      {
        test: /\.css$/,
        exclude: [/node_modules\/tinymce/, /node_modules\/@fi\/theme/],
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.(png|woff|woff2|eot|ttf|svg)$/,
        loader: 'file-loader',
        options: {
          name: 'files/[name]-[hash].[ext]',
        },
      },
    ]
  },
  target: 'web'
};
