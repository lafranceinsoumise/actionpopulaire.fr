import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  searchVotingLocation: "/api/procurations/communes-consulats/",
  createVotingProxyRequest: "/api/procurations/demande/",
  createVotingProxy: "/api/procurations/volontaire/",
};

export const getVotingProxyEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const searchVotingLocation = async (searchTerm) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getVotingProxyEndpoint("searchVotingLocation");
  try {
    const response = await axios.get(url, {
      params: { q: searchTerm },
    });
    result.data = response.data;
  } catch (e) {
    result.error = e.response?.data || { global: e.message };
  }

  return result;
};

export const createVotingProxyRequestOptions = async () => {
  const result = {
    data: null,
    error: null,
  };
  const url = getVotingProxyEndpoint("createVotingProxyRequest");
  try {
    const response = await axios.options(url);
    result.data = response.data?.actions?.POST;
  } catch (e) {
    if (e.response && e.response.data && Object.keys(e.response.data)[0]) {
      result.error = e.response.data[Object.keys(e.response.data)[0]];
    } else {
      if (e.response?.data && typeof e.response.data === "object") {
        result.error = e.response.data;
      } else {
        result.error = { global: e.message || "Une erreur est survenue" };
      }
    }
  }

  return result;
};

export const createVotingProxyRequest = async (data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getVotingProxyEndpoint("createVotingProxyRequest");
  const body = { ...data, votingLocation: undefined };
  if (data.votingLocation) {
    body[data.votingLocation.type] = data.votingLocation.value;
  }
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    if (e.response?.data && typeof e.response.data === "object") {
      result.error = e.response.data;
    } else {
      result.error = { global: e.message || "Une erreur est survenue" };
    }
  }

  return result;
};

export const createVotingProxyOptions = async () => {
  const result = {
    data: null,
    error: null,
  };
  const url = getVotingProxyEndpoint("createVotingProxy");
  try {
    const response = await axios.options(url);
    result.data = response.data?.actions?.POST;
  } catch (e) {
    if (e.response && e.response.data && Object.keys(e.response.data)[0]) {
      result.error = e.response.data[Object.keys(e.response.data)[0]];
    } else {
      if (e.response?.data && typeof e.response.data === "object") {
        result.error = e.response.data;
      } else {
        result.error = { global: e.message || "Une erreur est survenue" };
      }
    }
  }

  return result;
};

export const createVotingProxy = async (data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getVotingProxyEndpoint("createVotingProxy");
  const body = { ...data, votingLocation: undefined };
  if (data.votingLocation) {
    body[data.votingLocation.type] = data.votingLocation.value;
  }
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    if (e.response?.data && typeof e.response.data === "object") {
      result.error = e.response.data;
    } else {
      result.error = { global: e.message || "Une erreur est survenue" };
    }
  }

  return result;
};
