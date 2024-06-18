import axios from "@agir/lib/utils/axios";
import { addQueryStringParams } from "@agir/lib/utils/url";

export const ENDPOINT = {
  searchVotingLocation: "/api/elections/communes-consulats/",
  createVotingProxyRequest: "/api/procurations/demande/",
  retrieveUpdateVotingProxyRequest:
    "/api/procurations/demande/:votingProxyRequestPk/",
  createVotingProxy: "/api/procurations/volontaire/",
  retrieveUpdateVotingProxy: "/api/procurations/volontaire/:votingProxyPk/",
  replyToVotingProxyRequests:
    "/api/procurations/volontaire/:votingProxyPk/proposition/",
  votingProxyRequestsForProxy:
    "/api/procurations/volontaire/:votingProxyPk/demandes/",
  acceptedVotingProxyRequests: "/api/procurations/demande/reponse/",
  sendVotingProxyInformation:
    "/api/procurations/demande/:votingProxyRequestPk/volontaire/",
  confirmVotingProxyRequests: "/api/procurations/demande/confirmer/",
  cancelVotingProxyRequests: "/api/procurations/demande/annuler/",
  cancelVotingProxyRequestAcceptation: "/api/procurations/demande/se-desister/",
};

export const REPLY_ACTION = {
  ACCEPT: "accept",
  DECLINE: "decline",
};

export const getVotingProxyEndpoint = (key, params, searchParams) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  if (searchParams) {
    endpoint = addQueryStringParams(endpoint, searchParams, true);
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
    result.error = e.response?.data || { detail: e.message };
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
        result.error = { detail: e.message || "Une erreur est survenue" };
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
      result.error = { detail: e.message || "Une erreur est survenue" };
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
        result.error = { detail: e.message || "Une erreur est survenue" };
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
      result.error = { detail: e.message || "Une erreur est survenue" };
    }
  }

  return result;
};

export const replyToSingleVotingProxyRequest = async (
  action,
  votingProxy,
  request,
) => {
  const result = {
    data: null,
    error: null,
  };

  const url = getVotingProxyEndpoint("retrieveUpdateVotingProxyRequest", {
    votingProxyRequestPk: request.id,
  });

  const body = { action, votingProxy };

  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    if (e.response?.data && typeof e.response.data === "object") {
      result.error = { ...e.response.data, status: e.response.status };
    } else {
      result.error = { global: e.message || "Une erreur est survenue" };
    }
  }

  return result;
};

export const replyToVotingProxyRequests = async (
  action,
  votingProxyPk,
  requests,
) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getVotingProxyEndpoint("replyToVotingProxyRequests", {
    votingProxyPk,
  });
  const body = {
    action,
    votingProxyRequests: requests.map((request) => request.id),
  };
  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    if (e.response?.data && typeof e.response.data === "object") {
      result.error = { ...e.response.data, status: e.response.status };
    } else {
      result.error = { global: e.message || "Une erreur est survenue" };
    }
  }

  return result;
};

export const sendVotingProxyInformation = async (votingProxyRequests) => {
  const result = {
    data: null,
    error: null,
  };
  let votingProxyRequestPk = votingProxyRequests.find(
    (request) => request.status === "accepted" && request.proxy,
  );
  votingProxyRequestPk = votingProxyRequestPk?.id || votingProxyRequests[0].id;
  const url = getVotingProxyEndpoint("sendVotingProxyInformation", {
    votingProxyRequestPk,
  });
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    if (e.response?.data && typeof e.response.data === "object") {
      result.error = Object.values(e.response.data)[0];
    } else {
      result.error = { global: e.message || "Une erreur est survenue" };
    }
  }

  return result;
};

export const confirmVotingProxyRequests = async (votingProxyRequests) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getVotingProxyEndpoint("confirmVotingProxyRequests");
  const body = {
    votingProxyRequests: votingProxyRequests.map((request) => request.id),
  };
  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    if (e.response?.data && typeof e.response.data === "object") {
      result.error = Object.values(e.response.data)[0];
    } else {
      result.error = { global: e.message || "Une erreur est survenue" };
    }
  }

  return result;
};

export const cancelVotingProxyRequests = async (votingProxyRequests) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getVotingProxyEndpoint("cancelVotingProxyRequests");
  const body = {
    votingProxyRequests: votingProxyRequests.map((request) => request.id),
  };
  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    if (e.response?.data && typeof e.response.data === "object") {
      result.error = Object.values(e.response.data)[0];
    } else {
      result.error = { global: e.message || "Une erreur est survenue" };
    }
  }

  return result;
};

export const cancelVotingProxyRequestAcceptation = async (
  votingProxyRequests,
) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getVotingProxyEndpoint("cancelVotingProxyRequestAcceptation");
  const body = {
    votingProxyRequests: votingProxyRequests.map((request) => request.id),
  };
  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    if (e.response?.data && typeof e.response.data === "object") {
      result.error = Object.values(e.response.data)[0];
    } else {
      result.error = { global: e.message || "Une erreur est survenue" };
    }
  }

  return result;
};
