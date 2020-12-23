module.exports = {
  moduleNameMapper: {
    "\\.(css|scss|sass|less)$": "<rootDir>/jest/styleMock.js",
    "\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$":
      "<rootDir>/jest/fileMock.js",
    "^@agir/([a-zA-Z0-9_]+)/(.*)$": "<rootDir>/agir/$1/components/$2",
  },
  transformIgnorePatterns: [
    "/node_modules/(?!@babel/runtime-corejs3/helpers/esm/|path-to-regexp-es)",
    "\\.pnp\\.[^\\/]+$",
  ],
  // Automatically clear mock calls and instances between every test
  clearMocks: true,
  // An array of glob patterns indicating a set of files for which coverage information should be collected
  collectCoverageFrom: [
    "<rootDir>/agir/**/*.{js,jsx,mjs}",
    "!<rootDir>/agir/**/*.stories.{js,jsx}",
    "!<rootDir>/agir/**/*.test.{js,jsx}",
  ],
  // The directory where Jest should output its coverage files
  coverageDirectory: "<rootDir>/.coverage/jest",
  // An array of file extensions your modules use
  moduleFileExtensions: ["js", "json", "jsx"],
  // The paths to modules that run some code to configure or set up the testing environment before each test
  setupFilesAfterEnv: ["<rootDir>/jest/setup.js"],
  // The glob patterns Jest uses to detect test files
  testMatch: ["**/?(*.)+(test).js?(x)"],
  // An array of regexp pattern strings that are matched against all test paths, matched tests are skipped
  testPathIgnorePatterns: ["\\\\node_modules\\\\"],
  // Indicates whether each individual test should be reported during the run
  verbose: false,
};
