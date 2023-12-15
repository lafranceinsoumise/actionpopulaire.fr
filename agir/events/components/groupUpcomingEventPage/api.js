import querystring from "query-string";

export const ENDPOINT = {
  groupUpcomingEvents: "/api/evenements/groupes/",
};

export const getGroupUpcomignEventEndpoint = (
  key,
  params,
  querystringParams,
) => {
  let endpoint = ENDPOINT[key] || "";

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }

  if (querystringParams) {
    endpoint += `?${querystring.stringify(querystringParams, {
      arrayFormat: "comma",
    })}`;
  }

  return endpoint;
};
