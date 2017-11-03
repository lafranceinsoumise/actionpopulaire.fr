const path = require('path');

module.exports = {
    context: path.resolve(__dirname, 'src/javascript_components'),
    entry: {
        markdownEditor: './markdownEditor.js'
    },
    output: {
        libraryTarget: 'window',
        library: '[name]',
        filename: '[name].js',
        path: path.resolve(__dirname, 'src/assets/js')
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
                use: [
                    {loader: 'style-loader'},
                    {loader: 'css-loader'}
                ]
            }
        ]
    },
    target: 'web'
};
