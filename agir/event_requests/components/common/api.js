import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  getEventSpeaker: "/api/evenements/demandes/intervenant-e/",
  getEventSpeakerUpcomingEvents:
    "/api/evenements/demandes/intervenant-e/evenements-a-venir/",
  patchEventSpeaker: "/api/evenements/demandes/intervenant-e/",
  patchEventSpeakerRequest:
    "/api/evenements/demandes/disponibilite/:eventSpeakerRequestId/",
};

export const getEventRequestEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const patchEventSpeaker = async (data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getEventRequestEndpoint("patchEventSpeaker");
  try {
    const response = await axios.patch(url, data);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const patchEventSpeakerRequest = async (data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getEventRequestEndpoint("patchEventSpeakerRequest", {
    eventSpeakerRequestId: data.id,
  });
  try {
    const response = await axios.patch(url, {
      available: data.available,
      comment: data.comment,
    });
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
