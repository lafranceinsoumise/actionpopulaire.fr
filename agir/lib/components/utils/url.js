export const parseURL = (url) => new URL(url);

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
  let parsedURL = url;
  try {
    parsedURL = parseURL(url);
    Object.entries(params).forEach(([key, value]) => {
      parsedURL.searchParams.set(key, value);
    });
    return parsedURL.toString();
  } catch (e) {
    Object.entries(params).forEach(([key, value], i) => {
      if (value) {
        parsedURL += `${i === 0 ? "?" : "&"}${encodeURIComponent(
          key
        )}=${encodeURIComponent(value)}`;
      }
    });
    return parsedURL;
  }
};
