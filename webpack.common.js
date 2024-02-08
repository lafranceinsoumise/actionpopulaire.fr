const fs = require("fs");
const glob = require("glob");
const path = require("path");

require("dotenv").config({
  path: path.join(__dirname, ".env"),
});

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { InjectManifest } = require("workbox-webpack-plugin");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const StatoscopeWebpackPlugin = require("@statoscope/webpack-plugin").default;
const TerserPlugin = require("terser-webpack-plugin");
const WebpackBar = require("webpackbar");

const packageConfig = require(path.resolve(__dirname, "package.json"));
const DISTPATH = path.resolve(__dirname, "assets/");

const isDirectory = (f) => fs.statSync(f).isDirectory();
const directoryHasFile = (f) => (d) => fs.readdirSync(d).includes(f);

const COREJS_VERSION = packageConfig.dependencies["core-js"];

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
      .map((f) => [path.basename(dir), path.resolve(dir, "components", f)]),
  )
  .filter(([_app, f]) =>
    isDirectory(f) ? directoryHasFile("index.js")(f) : f.endsWith(".js"),
  )
  .map(([app, f]) => [app + "/" + path.basename(f, ".js"), f])
  .reduce((obj, [name, file]) => {
    obj[name] = file;
    return obj;
  }, {});

// create import aliases with the django app names leading to their `components` folders
const aliases = applications.reduce((obj, app) => {
  obj["@agir/" + path.basename(app) + "/data"] = path.resolve(app, "data/");
  obj["@agir/" + path.basename(app)] = path.resolve(app, "components/");
  return obj;
}, {});

// Generate an HTML fragment with all chunks tag for each entry
const htmlPlugins = (type) => [
  new HtmlWebpackPlugin({
    filename: `includes/theme.bundle.html`,
    inject: false,
    chunks: ["theme"],
    templateContent: ({ htmlWebpackPlugin }) =>
      `<link href="${htmlWebpackPlugin.files.css[0]}" rel="stylesheet">`,
  }),
  ...Object.keys(components).map(
    (entry) =>
      new HtmlWebpackPlugin({
        filename: `includes/${entry}.${
          type === CONFIG_TYPES.ES2015 ? "modules" : "bundle"
        }.html`,
        scriptLoading: type === CONFIG_TYPES.ES5 ? "defer" : "module",
        inject: false,
        cache: false,
        chunks: [entry],
        templateContent: ({ htmlWebpackPlugin }) =>
          type === CONFIG_TYPES.ES5
            ? htmlWebpackPlugin.files.js
                .map((file) => `<script nomodule src="${file}"></script>`)
                .join("") + `{% include "${entry}.modules.html" %}`
            : htmlWebpackPlugin.tags.headTags + htmlWebpackPlugin.tags.bodyTags,
      }),
  ),
];

// List all chunks on which main app depends for preloading by service worker
let _cachedAppEntryFiles;
const getAppEntryFiles = (compilation) => {
  _cachedAppEntryFiles =
    _cachedAppEntryFiles ||
    compilation.namedChunkGroups
      .get("front/app")
      .chunks.map((c) => Array.from(c.files))
      .flat();

  return _cachedAppEntryFiles;
};

// List all chunks on which other apps depends for preload and chunking exclusion if not in main app
const OTHER_ENTRIES = [
  "cagnottes/progress",
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
  "lib/multiDateField",
  "lib/emojiField",
  "theme",
];

let _cachedOtherEntryFiles;

const getOtherEntryFiles = (compilation) => {
  _cachedOtherEntryFiles =
    _cachedOtherEntryFiles ||
    OTHER_ENTRIES.map((name) =>
      compilation.namedChunkGroups
        .get(name)
        .chunks.map((c) => Array.from(c.files))
        .flat(),
    )
      .flat()
      .filter((file) => !getAppEntryFiles(compilation).includes(file));

  return _cachedOtherEntryFiles;
};

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
      cacheDirectory: path.join(
        process.env.BABEL_CACHE_DIRECTORY ||
          "node_modules/.cache/babel-loader/",
        type,
      ),
      exclude: [/core-js/, /regenerator-runtime/, /webpack[\\/]buildin/],
      presets: [
        "@babel/preset-react",
        type === CONFIG_TYPES.ES5
          ? [
              "@babel/preset-env",
              {
                bugfixes: true,
                loose: true,
                modules: "auto",
                useBuiltIns: "usage",
                corejs: { version: COREJS_VERSION },
                targets: {
                  browsers: [
                    "> 0.5% in FR",
                    "last 2 versions",
                    "Firefox ESR",
                    "not dead",
                    "not IE 11",
                    "safari > 12",
                  ],
                },
                include: ["@babel/plugin-proposal-class-properties"],
              },
            ]
          : [
              "babel-preset-env-modules",
              {
                development: type === CONFIG_TYPES.DEV,
                modules: false,
                include: ["@babel/plugin-proposal-class-properties"],
              },
            ],
      ],
      plugins: [
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
  name: type,
  context: path.resolve(__dirname, "agir/"),
  entry: Object.assign(
    {
      theme: path.resolve(__dirname, "agir/front/components/theme/theme.scss"),
    },
    components,
  ),
  plugins: [
    ...htmlPlugins(type),
    new MiniCssExtractPlugin({ filename: "static/css/[name]-[chunkhash].css" }),
    type !== CONFIG_TYPES.DEV &&
      new webpack.IgnorePlugin({
        resourceRegExp: /^\.\/locale$/,
        contextRegExp: /moment$/,
      }),
    type === CONFIG_TYPES.ES2015 &&
      new InjectManifest({
        swSrc: path.resolve(
          __dirname,
          "agir/front/components/serviceWorker/serviceWorker.js",
        ),
        swDest: "static/service-worker.js",
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
      }),
    new webpack.EnvironmentPlugin({
      WEBPUSH_PUBLIC_KEY: "",
      SENTRY_RELEASE:
        type !== CONFIG_TYPES.DEV
          ? require("child_process")
              .execSync("git rev-parse HEAD")
              .toString()
              .replace("\n", "")
          : "",
      SENTRY_ENV: type !== CONFIG_TYPES.DEV ? "production" : "",
      DEBUG: type === CONFIG_TYPES.DEV ? "agir:*" : "",
      ENABLE_VENDOR_PREFIXES: type === CONFIG_TYPES.ES5,
    }),
    type !== CONFIG_TYPES.DEV &&
      new WebpackBar({
        name: type,
        color: type === CONFIG_TYPES.ES2015 ? "#cbbfec" : "#fcfbd9",
      }),
    type === CONFIG_TYPES.ES2015 &&
      new StatoscopeWebpackPlugin({
        saveReportTo: `.coverage/statoscope/[name].html`,
        saveStatsTo: `.coverage/statoscope/[name]-[hash].json`,
        additionalStats: glob.sync(".coverage/statoscope/*.json"),
        normalizeStats: true,
        compressor: false,
        watchMode: false,
        open: false,
        name: type,
        data: () => fetchAsyncData(),
        reports: [
          {
            id: "top-50-biggest-modules",
            name: "Top 50 biggest modules",
            view: [
              "struct",
              {
                data: `#.stats.compilations.sort(time desc)[0].(
                  $compilation: $;
                    modules.({
                      module: $,
                      hash: $compilation.hash,
                      size: getModuleSize($compilation.hash)
                    })
                  ).sort(size.size desc)[:50]`,
                view: "list",
                item: "module-item",
              },
            ],
          },
        ],
      }),
  ].filter(Boolean),
  output: {
    libraryTarget: "window",
    library: ["Agir", "[name]"],
    filename: `static/components/[name]-[chunkhash].${
      type === CONFIG_TYPES.ES2015 ? "mjs" : "js"
    }?cv=7`,
    path: DISTPATH,
    clean: type === CONFIG_TYPES.DEV,
    assetModuleFilename: "static/files/[hash][ext][query]",
  },
  module: {
    rules: [
      {
        test: /swiper\.esm\.js/,
        sideEffects: false,
      },
      configureBabelLoader(type),
      {
        test: /theme\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader",
          {
            loader: "sass-loader",
            options: {
              sassOptions: {
                quietDeps: true,
              },
            },
          },
        ],
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
        test: /\.(jpg|jpeg|png|woff|woff2|eot|ttf|svg|webp)$/,
        exclude: [new RegExp("node_modules\\" + path.sep + "tinymce")],
        type: "asset/resource",
      },
    ],
  },
  optimization: {
    runtimeChunk: "single",
    splitChunks: {
      chunks: "all",
      cacheGroups: {
        emojiMart: {
          test: /[\\/]node_modules[\\/]@emoji-mart[\\/]/,
          name: "em",
          chunks: "all",
        },
        openlayers: {
          test: /[\\/]node_modules[\\/]ol[\\/]/,
          name: "ol",
          chunks: "all",
        },
        quill: {
          test: /[\\/]node_modules[\\/](quill|react-quill)[\\/]/,
          name: "ql",
          chunks: "all",
        },
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: "rt",
          chunks: "all",
        },
        sentry: {
          test: /[\\/]node_modules[\\/]@sentry[\\/]/,
          name: "sy",
          chunks: "all",
        },
        "style-components": {
          test: /[\\/]node_modules[\\/]styled-components[\\/]/,
          name: "sc",
          chunks: "all",
        },
      },
    },
    moduleIds: "deterministic",
    minimize: type !== CONFIG_TYPES.DEV,
    minimizer: [
      new TerserPlugin({
        test: /\.m?js(\?.*)?$/i,
        terserOptions: {
          ecma: 8,
          safari10: true,
        },
      }),
    ],
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
