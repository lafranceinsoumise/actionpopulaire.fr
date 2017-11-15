const path = require('path');
const UglifyJSWebpackPlugin = require('uglifyjs-webpack-plugin')

module.exports = {
    context: path.resolve(__dirname, 'src/javascript_components'),
    entry: {
        richEditor: './richEditor.js'
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
                        presets: ['babel-preset-env']
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
    plugins: [
        new UglifyJSWebpackPlugin()
    ],
    target: 'web'
};
