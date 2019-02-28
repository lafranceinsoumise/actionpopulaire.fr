const path = require("path");
const fs = require("fs");

const CleanWebpackPlugin = require("clean-webpack-plugin");
const BundleTracker = require("webpack-bundle-tracker");
const BundleAnalyzerPlugin = require("webpack-bundle-analyzer")
  .BundleAnalyzerPlugin;
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const webpack = require("webpack");

const DISTPATH = path.resolve(__dirname, "assets/components");
const cssName = require("@fi/theme/dist/assets.json")["main.css"];
const apiEndpoint = JSON.stringify(process.env.API_ENDPOINT || "/legacy");

const flatten = array => array.reduce((acc, curr) => acc.concat(curr));
const isDirectory = f => fs.statSync(f).isDirectory();
const directoryHasFile = f => d => fs.readdirSync(d).includes(f);

// establish the list of Django applications with a `components` folder
const applications = fs
  .readdirSync(path.resolve(__dirname, "agir"))
  .map(f => path.resolve(__dirname, "agir", f))
  .filter(isDirectory)
  .filter(directoryHasFile("components"));

// javascript components are either:
// - directories with an index.js
// - .js files
// that are directly found in a `components` folder of one of the django apps.
//
// The bundle name will be `<django app name>/<name of directory / .js file>`
const components = flatten(
  applications.map(dir =>
    fs
      .readdirSync(path.resolve(dir, "components"))
      .map(f => [path.basename(dir), path.resolve(dir, "components", f)])
  )
)
  .filter(
    ([_app, f]) =>
      (isDirectory(f) && directoryHasFile("index.js")(f)) || f.endsWith(".js")
  )
  .map(([app, f]) => [app + "/" + path.basename(f, ".js"), f])
  .reduce((obj, [name, file]) => {
    obj[name] = file;
    return obj;
  }, {});

// create import aliases with the django app names leading to their `components` folders
const aliases = applications.reduce((obj, app) => {
  obj["@agir/" + path.basename(app)] = path.resolve(app, "components") + "/";
  return obj;
}, {});

module.exports = {
  context: path.resolve(__dirname, "agir/"),
  entry: Object.assign(
    {
      theme: "@fi/theme/dist/styles/" + cssName
    },
    components
  ),
  plugins: [
    new CleanWebpackPlugin([DISTPATH]),
    new BundleTracker({ path: DISTPATH }),
    new MiniCssExtractPlugin(),
    new webpack.DefinePlugin({ API_ENDPOINT: apiEndpoint }),
    new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
    new BundleAnalyzerPlugin({ analyzerMode: "static", openAnalyzer: false })
  ],
  output: {
    libraryTarget: "window",
    library: "[name]",
    filename: "[name]-[chunkhash].js",
    path: DISTPATH
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: "babel-loader?cacheDirectory=true"
        }
      },
      {
        test: new RegExp("@fi/theme/dist/styles/" + cssName),
        use: [MiniCssExtractPlugin.loader, "css-loader"]
      },
      {
        test: /\.css$/,
        exclude: [/node_modules\/tinymce/, /node_modules\/@fi\/theme/],
        use: ["style-loader", "css-loader"]
      },
      {
        test: /\.(png|woff|woff2|eot|ttf|svg)$/,
        exclude: [/node_modules\/tinymce/],
        loader: "file-loader",
        options: {
          name: "[name]-[hash].[ext]",
          outputPath: "files"
        }
      }
    ]
  },
  target: "web",
  resolve: {
    alias: aliases,
    modules: ["node_modules"]
  },
  watchOptions: {
    ignored: /node_modules/
  }
};
