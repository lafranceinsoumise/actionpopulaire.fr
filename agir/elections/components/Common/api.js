import axios from "@agir/lib/utils/axios";
import { addQueryStringParams } from "@agir/lib/utils/url";

export const ENDPOINT = {
  searchVotingLocation: "/api/elections/communes-consulats/",
  searchPollingStations: "/api/elections/bureaux-de-vote/:commune/",
  getCirconscriptionsLegislatives:
    "/api/elections/circonscriptions-legislatives/",
  pollingStationOfficer: "/api/elections/assesseure-deleguee/",
};

export const getElectionEndpoint = (key, params, searchParams) => {
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
  const url = getElectionEndpoint("searchVotingLocation");
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

export const searchPollingStations = async (commune) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getElectionEndpoint("searchPollingStations", { commune });
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = e.response?.data || { detail: e.message };
  }

  return result;
};

export const getCirconscriptionsLegislatives = async () => {
  const result = {
    data: null,
    error: null,
  };
  const url = getElectionEndpoint("getCirconscriptionsLegislatives");
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = e.response?.data || { detail: e.message };
  }

  return result;
};

export const createPollingStationOfficerOptions = async () => {
  const result = {
    data: null,
    error: null,
  };
  const url = getElectionEndpoint("pollingStationOfficer");
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

export const createPollingStationOfficer = async (data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getElectionEndpoint("pollingStationOfficer");
  const body = {
    ...data,
    votingCommune: null,
    votingConsulate: null,
    votingLocation: undefined,
    votingCirconscriptionLegislative:
      data?.votingCirconscriptionLegislative?.code || undefined,
  };
  if (data.votingLocation?.type === "commune") {
    body.votingCommune = data.votingLocation.value;
  } else if (data.votingLocation?.type === "consulate") {
    body.votingConsulate = data.votingLocation.value;
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
