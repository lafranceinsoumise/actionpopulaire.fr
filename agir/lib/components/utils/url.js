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
