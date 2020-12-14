import URI from "urijs";

export const parseURI = (uri) => new URI(uri);

export const addQueryStringParams = (uri, params = {}) => {
  if (!uri) {
    return "";
  }
  if (
    !params ||
    typeof params !== "object" ||
    Object.keys(params).lenght === 0
  ) {
    return uri;
  }
  const parsedURI = parseURI(uri).search((data) => ({
    ...data,
    ...params,
  }));

  return parsedURI.href();
};
