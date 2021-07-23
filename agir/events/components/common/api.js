import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  getEvent: "/api/evenements/:eventPk/",
  rsvpEvent: "/api/evenements/:eventPk/inscription/",
  quitEvent: "/api/evenements/:eventPk/inscription/",

  getParticipants: "/api/evenements/:eventPk/participants/",
  updateEvent: "/api/evenements/:eventPk/update/",
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

export const updateEvent = async (eventPk, data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getEventEndpoint("updateEvent", { eventPk });
  let headers = undefined;
  let body = data;

  if (body.image || body.compteRenduPhotos?.length > 0) {
    body = new FormData();
    Object.keys(data).forEach((e) => {
      body.append(e, data[e]);
    });
    headers = {
      "content-type": "multipart/form-data",
    };
  }

  console.log("formData to update event :", data);
  return;

  try {
    const response = await axios.patch(url, body, { headers });
    result.data = response.data;
  } catch (e) {
    if (e.response && e.response.data) {
      result.error =
        e.response.status === 400 && data.image
          ? { image: "La taille du fichier ne doit pas dépasser le 2.5 Mo" }
          : e.response.data;
    } else {
      result.error = e.message;
    }
  }

  return result;
};
