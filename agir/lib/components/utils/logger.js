import debug from "debug";

const generateLogger = (filename) => ({
  debug: debug(`agir:${filename.replace("/", ":").replace(".js", "")}`),
  warn: console.warn.bind(console),
  info: console.info.bind(console),
  error: console.error.bind(console),
});

export default generateLogger;
