import debug from "debug";

const generateLogger = (filename) => ({
  debug: debug(`agir:${filename.replace("/", ":").replace(".js", "")}`),
  warn: console.warn,
  info: console.info,
  error: console.error,
});

export default generateLogger;
