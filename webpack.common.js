const path = require('path');


module.exports = {
  context: path.resolve(__dirname, 'src/javascript_components'),
  entry: {
    richEditor: './richEditor.js',
    helpDialog: './helpDialog.js'
  },
  output: {
    libraryTarget: 'window',
    library: '[name]',
    filename: '[name].js',
    path: path.resolve(__dirname, 'src/assets/components')
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
