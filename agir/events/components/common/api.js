import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  getEvent: "/api/evenements/:eventPk/",
  rsvpEvent: "/api/evenements/:eventPk/inscription/",
  quitEvent: "/api/evenements/:eventPk/inscription/",
};

export const getEventEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const rsvpEvent = async (eventPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getEventEndpoint("rsvpEvent", { eventPk });
  const body = {};
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const quitEvent = async (eventPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getEventEndpoint("quitEvent", { eventPk });
  try {
    const response = await axios.delete(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
