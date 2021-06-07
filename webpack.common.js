const path = require("path");
const fs = require("fs");

require("dotenv").config({
  path: path.join(__dirname, ".env"),
});

const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const BundleAnalyzerPlugin =
  require("webpack-bundle-analyzer").BundleAnalyzerPlugin;
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { InjectManifest } = require("workbox-webpack-plugin");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const WebpackBar = require("webpackbar");

const DISTPATH = path.resolve(__dirname, "assets/components");

const isDirectory = (f) => fs.statSync(f).isDirectory();
const directoryHasFile = (f) => (d) => fs.readdirSync(d).includes(f);

// establish the list of Django applications with a `components` folder
const applications = fs
  .readdirSync(path.resolve(__dirname, "agir"))
  .map((f) => path.resolve(__dirname, "agir", f))
  .filter(isDirectory)
  .filter(directoryHasFile("components"));

// javascript components are either:
// - directories with an index.js
// - .js files
// that are directly found in a `components` folder of one of the django apps.
//
// The bundle name will be `<django app name>/<name of directory / .js file>`
const components = applications
  .flatMap((dir) =>
    fs
      .readdirSync(path.resolve(dir, "components"))
      .map((f) => [path.basename(dir), path.resolve(dir, "components", f)])
  )
  .filter(([_app, f]) =>
    isDirectory(f) ? directoryHasFile("index.js")(f) : f.endsWith(".js")
  )
  .map(([app, f]) => [app + "/" + path.basename(f, ".js"), f])
  .reduce((obj, [name, file]) => {
    obj[name] = file;
    return obj;
  }, {});

// create import aliases with the django app names leading to their `components` folders
const aliases = applications.reduce((obj, app) => {
  obj["@agir/" + path.basename(app)] = path.resolve(app, "components/");
  return obj;
}, {});

// Generate an HTML fragment with all chunks tag for each entry
const htmlPlugins = Object.keys(components).map(
  (entry) =>
    new HtmlWebpackPlugin({
      filename: `includes/${entry}.bundle.html`,
      scriptLoading: "blocking",
      inject: false,
      chunks: [entry],
      templateContent: ({ htmlWebpackPlugin }) =>
        htmlWebpackPlugin.tags.headTags + htmlWebpackPlugin.tags.bodyTags,
    })
);

// List all chunks on which main app depends for preloading by service worker
let _cachedAppEntryFiles;
const getAppEntryFiles = (compilation) => {
  if (_cachedAppEntryFiles) {
    return _cachedAppEntryFiles;
  }

  _cachedAppEntryFiles = compilation.namedChunkGroups
    .get("front/app")
    .chunks.map((c) => Array.from(c.files))
    .flat();

  return _cachedAppEntryFiles;
};

// List all chunks on which other apps depends for preload exclusion if not in main app
let _cachedOtherEntryFiles;
const getOtherEntryFiles = (compilation) => {
  if (_cachedOtherEntryFiles) {
    return _cachedOtherEntryFiles;
  }

  _cachedOtherEntryFiles = [
    "donations/donationForm",
    "donations/spendingRequestLib",
    "elus/parrainages",
    "front/legacyPages",
    "front/richEditor",
    "groups/groupSelector",
    "lib/adminJsonWidget",
    "lib/communeField",
    "lib/creationForms",
    "lib/IBANField",
    "lib/locationSearchField",
    "theme",
  ]
    .map((name) =>
      compilation.namedChunkGroups
        .get(name)
        .chunks.map((c) => Array.from(c.files))
        .flat()
    )
    .flat();

  return _cachedOtherEntryFiles;
};

module.exports = {
  context: path.resolve(__dirname, "agir/"),
  entry: Object.assign(
    {
      theme: path.resolve(__dirname, "agir/front/components/theme/theme.scss"),
    },
    components
  ),
  plugins: [
    new WebpackBar(),
    ...htmlPlugins,
    new HtmlWebpackPlugin({
      filename: `includes/theme.bundle.html`,
      inject: false,
      chunks: ["theme"],
      templateContent: ({ htmlWebpackPlugin }) =>
        `<link href="${htmlWebpackPlugin.files.css[0]}" rel="stylesheet">`,
    }),
    new CleanWebpackPlugin(),
    new MiniCssExtractPlugin({ filename: "[name]-[chunkhash].css" }),
    new webpack.IgnorePlugin(
      new RegExp("^.\\" + path.sep + "locale$"),
      /moment$/
    ),
    new BundleAnalyzerPlugin({ analyzerMode: "static", openAnalyzer: false }),
    new InjectManifest({
      swSrc: path.resolve(
        __dirname,
        "agir/front/components/serviceWorker/serviceWorker.js"
      ),
      swDest: "service-worker.js",
      maximumFileSizeToCacheInBytes: 7000000,
      include: [
        ({ asset, compilation }) => {
          const mainAppEntryFiles = getAppEntryFiles(compilation);
          const otherEntryFiles = getOtherEntryFiles(compilation);

          return (
            mainAppEntryFiles.includes(asset.name) ||
            !(
              otherEntryFiles.includes(asset.name) ||
              [/front\/skins/, /\.html$/, /\.LICENSE.txt/].some((excluded) =>
                excluded.test(asset.name)
              )
            )
          );
        },
      ],
    }),
    new webpack.EnvironmentPlugin(["WEBPUSH_PUBLIC_KEY"]),
  ],
  output: {
    libraryTarget: "window",
    library: ["Agir", "[name]"],
    filename: "[name]-[chunkhash].js",
    path: DISTPATH,
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        include: [
          path.resolve(__dirname, "agir"),
          path.resolve(__dirname, "node_modules/react-spring"),
        ],
        exclude: [new RegExp("node_modules\\" + path.sep)],
        use: {
          loader: "babel-loader",
          options: {
            cacheDirectory: process.env.BABEL_CACHE_DIRECTORY || true,
          },
        },
      },
      {
        test: /theme\.scss$/,
        use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"],
      },
      {
        test: /\.scss$/,
        exclude: [new RegExp("theme\\" + path.sep + "theme.scss")],
        use: [
          "style-loader",
          {
            loader: "css-loader",
            options: {
              modules: { compileType: "icss", auto: /\.scss$/i },
            },
          },
          "sass-loader",
        ],
      },
      {
        test: /\.css$/,
        exclude: [new RegExp("node_modules\\" + path.sep + "tinymce")],
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.(jpg|jpeg|png|woff|woff2|eot|ttf|svg)$/,
        exclude: [new RegExp("node_modules\\" + path.sep + "tinymce")],
        type: "asset/resource",
      },
    ],
  },
  optimization: {
    splitChunks: {
      chunks: "all",
    },
  },
  target: "web",
  resolve: {
    alias: aliases,
    modules: ["node_modules"],
  },
  node: {
    __filename: true,
  },
  watchOptions: {
    ignored: /node_modules/,
  },
};
