export const parseURL = (url) =>
  new URL(url, window.location && window.location.origin);

export const addQueryStringParams = (url, params = {}) => {
  if (!url) {
    return "";
  }
  if (
    !params ||
    typeof params !== "object" ||
    Object.keys(params).length === 0
  ) {
    return url;
  }
  try {
    let parsedURL = url;
    parsedURL = parseURL(url);
    Object.entries(params).forEach(([key, value]) => {
      parsedURL.searchParams.set(key, value);
    });
    return parsedURL.toString();
  } catch (e) {
    return url;
  }
};

export const parseQueryStringParams = (url) => {
  const params = {};
  let queryString = url ? url.split("?")[1] : window.location.search.slice(1);
  if (!queryString) {
    return params;
  }

  queryString = queryString.split("#")[0];
  queryString.split("&").forEach((entry) => {
    // separate the keys and the values
    let [key, value] = entry.split("=");
    value = typeof value === "undefined" ? true : value;

    if (key.match(/\[(\d+)?\]$/)) {
      const name = key.replace(/\[(\d+)?\]/, "");
      params[name] = params[name] || [];
      if (name.match(/\[\d+\]$/)) {
        var index = /\[(\d+)\]/.exec(key)[1];
        params[name][index] = value;
      } else {
        params[name].push(value);
      }
    } else {
      if (!params[key]) {
        params[key] = value;
      } else if (params[key] && typeof params[key] === "string") {
        params[key] = [params[key]];
        params[key].push(value);
      } else {
        params[key].push(value);
      }
    }
  });

  return params;
};
