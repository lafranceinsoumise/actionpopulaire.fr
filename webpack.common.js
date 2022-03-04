const path = require("path");
const fs = require("fs");

require("dotenv").config({
  path: path.join(__dirname, ".env"),
});

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

const CONFIG_TYPES = {
  ES2015: "es2015+",
  ES5: "es5",
  DEV: "dev",
};

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
const aliases = applications.reduce(
  (obj, app) => {
    obj["@agir/" + path.basename(app)] = path.resolve(app, "components/");
    return obj;
  },
  {
    luxon: "luxon/src/luxon",
  }
);

// Generate an HTML fragment with all chunks tag for each entry
const htmlPlugins = (type) =>
  Object.keys(components).map(
    (entry) =>
      new HtmlWebpackPlugin({
        filename: `includes/${entry}.${
          type === CONFIG_TYPES.ES2015 ? "modules" : "bundle"
        }.html`,
        scriptLoading: "defer",
        inject: false,
        chunks: [entry],
        templateContent: ({ htmlWebpackPlugin }) => {
          switch (type) {
            case CONFIG_TYPES.DEV:
              return (
                htmlWebpackPlugin.tags.headTags +
                htmlWebpackPlugin.tags.bodyTags
              );
            case CONFIG_TYPES.ES2015:
              return htmlWebpackPlugin.files.js
                .map((file) => `<script type="module" src="${file}"></script>`)
                .join("");
            case CONFIG_TYPES.ES5:
              return (
                htmlWebpackPlugin.files.js
                  .map((file) => `<script nomodule src="${file}"></script>`)
                  .join("") + `{% include "${entry}.modules.html" %}`
              );
          }
        },
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

  _cachedOtherEntryFiles = _cachedOtherEntryFiles.filter(
    (file) => !getAppEntryFiles(compilation).includes(file)
  );

  return _cachedOtherEntryFiles;
};

const es5Browsers = [
  "> 0.5% in FR",
  "last 2 versions",
  "Firefox ESR",
  "not dead",
  "not IE 11",
];

const es2015Browsers = { esmodules: true };

const configureBabelLoader = (type) => ({
  test: /\.m?js$/,
  include: [
    path.resolve(__dirname, "agir"),
    type === CONFIG_TYPES.ES2015
      ? undefined
      : path.resolve(__dirname, "node_modules/react-spring"),
  ].filter(Boolean),
  exclude:
    type === CONFIG_TYPES.ES2015
      ? []
      : [new RegExp("node_modules\\" + path.sep)],
  use: {
    loader: "babel-loader",
    options: {
      cacheDirectory: process.env.BABEL_CACHE_DIRECTORY || true,
      exclude: [/core-js/, /regenerator-runtime/, /webpack[\\/]buildin/],
      presets: [
        "@babel/preset-react",
        [
          "@babel/preset-env",
          {
            modules: false,
            corejs: "3.20",
            useBuiltIns: "usage",
            targets: type === CONFIG_TYPES.ES5 ? es5Browsers : es2015Browsers,
          },
        ],
      ],
      plugins: [
        "@babel/plugin-syntax-dynamic-import",
        [
          "babel-plugin-styled-components",
          {
            // This option enhances the attached CSS class name on each component with richer output to help identify your components in the DOM.
            displayName: type === CONFIG_TYPES.DEV,
            // Remove comments and whitespace from the CSS.
            minify: type !== CONFIG_TYPES.DEV,
            // Transpile tagged template literals into optimized code.
            transpileTemplateLiterals: type !== CONFIG_TYPES.DEV,
            // By default minifiers cannot properly perform dead code elimination on styled components because they are assumed to have side effects. This enables "pure annotations" to tell the compiler that they do not have side effects.
            pure: type !== CONFIG_TYPES.DEV,
            // Enable SSR optimization
            ssr: false,
          },
        ],
        ["@babel/plugin-transform-runtime", { useESModules: true }],
        type === CONFIG_TYPES.DEV
          ? require.resolve("react-refresh/babel")
          : undefined,
        type !== CONFIG_TYPES.DEV
          ? [
              "transform-react-remove-prop-types",
              {
                removeImport: true,
              },
            ]
          : undefined,
      ].filter(Boolean),
    },
  },
});

module.exports = (type = CONFIG_TYPES.ES5) => ({
  context: path.resolve(__dirname, "agir/"),
  entry: Object.assign(
    {
      theme: path.resolve(__dirname, "agir/front/components/theme/theme.scss"),
    },
    components
  ),
  plugins: [
    type !== CONFIG_TYPES.DEV && new WebpackBar(),
    ...htmlPlugins(type),
    new HtmlWebpackPlugin({
      filename: `includes/theme.bundle.html`,
      inject: false,
      chunks: ["theme"],
      templateContent: ({ htmlWebpackPlugin }) =>
        `<link href="${htmlWebpackPlugin.files.css[0]}" rel="stylesheet">`,
    }),
    new MiniCssExtractPlugin({ filename: "[name]-[chunkhash].css" }),
    type !== CONFIG_TYPES.DEV &&
      new webpack.IgnorePlugin({
        resourceRegExp: /^\.\/locale$/,
        contextRegExp: /moment$/,
      }),
    type !== CONFIG_TYPES.DEV &&
      new BundleAnalyzerPlugin({
        analyzerMode: "static",
        openAnalyzer: false,
        reportFilename:
          type === CONFIG_TYPES.ES2015 ? "es2015_report.html" : "report.html",
        reportTitle:
          type === CONFIG_TYPES.ES2015
            ? "es2015+ webpack build report"
            : "es5 webpack build report",
      }),
    type === CONFIG_TYPES.ES2015
      ? new InjectManifest({
          swSrc: path.resolve(
            __dirname,
            "agir/front/components/serviceWorker/serviceWorker.js"
          ),
          swDest: "service-worker.js",
          maximumFileSizeToCacheInBytes: 7000000,
          mode: "production",
          exclude: [
            new RegExp("skins\\" + path.sep),
            /\.html$/,
            /\.LICENSE.txt$/,
            /\.mjs.map/,
            /\.css.map/,
            ({ asset, compilation }) =>
              getOtherEntryFiles(compilation).includes(asset.name),
          ],
        })
      : null,
    new webpack.EnvironmentPlugin(["WEBPUSH_PUBLIC_KEY"]),
  ].filter(Boolean),
  output: {
    libraryTarget: "window",
    library: ["Agir", "[name]"],
    filename: `[name]-[chunkhash].${
      type === CONFIG_TYPES.ES2015 ? "mjs" : "js"
    }?cv=3`,
    path: DISTPATH,
  },
  module: {
    rules: [
      configureBabelLoader(type),
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
              modules: { mode: "icss", auto: /\.scss$/i },
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
});

module.exports.CONFIG_TYPES = CONFIG_TYPES;
