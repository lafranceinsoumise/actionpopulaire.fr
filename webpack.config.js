const path = require('path');

module.exports = {
    context: path.resolve(__dirname, 'src/javascript_components'),
    entry: {
        richEditor: 'imports-loader?jQuery=jquery,this=>window!./richEditor.js'
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
                use: [
                    {loader: 'style-loader'},
                    {loader: 'css-loader'}
                ]
            },
            {
                test: /\.svg$/,
                use: {
                    loader: 'file-loader',
                    options: {publicPath: '/static/components/', outputPath: 'images/'}
                }
            }
        ]
    },
    target: 'web'
};
