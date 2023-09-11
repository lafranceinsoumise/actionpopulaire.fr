import { DateTime } from "luxon";

import axios from "@agir/lib/utils/axios";
import { objectToFormData } from "@agir/lib/utils/forms";
import { addQueryStringParams } from "@agir/lib/utils/url";

export const ENDPOINT = {
  getEventCard: "/api/evenements/:eventPk/",
  getEvent: "/api/evenements/:eventPk/details/",
  rsvpEvent: "/api/evenements/:eventPk/inscription/",
  quitEvent: "/api/evenements/:eventPk/inscription/:groupPk/",
  joinEventAsGroup: "/api/evenements/:eventPk/inscription-groupe/",

  eventPropertyOptions: "/api/evenements/options/",
  createEvent: "/api/evenements/creer/",
  updateEvent: "/api/evenements/:eventPk/modifier/",
  getEventMessages: "/api/evenements/:eventPk/messages/",
  eventProjects: "/api/evenements/projets/",
  eventProject: "/api/evenements/:eventPk/projet/",
  addEventProjectDocument: "/api/evenements/:eventPk/projet/document/",
  getDetailAdvanced: "/api/evenements/:eventPk/details-avances/",
  addOrganizer: "/api/evenements/:eventPk/organisateurs/",
  inviteGroupOrganizer: "/api/evenements/:eventPk/groupes-organisateurs/",
  getOrganizerGroupSuggestions:
    "/api/evenements/:eventPk/groupes-organisateurs/",
  cancelEvent: "/api/evenements/:eventPk/annuler/",
  updateLocation: "/evenements/:eventPk/localisation/",

  getEventReportForm: "/api/evenements/:eventPk/bilan/",
  getEventAssets: "/api/evenements/:eventPk/visuels/",

  getOrganizedEvents: "/api/evenements/organises/",
};

export const getEventEndpoint = (key, params, searchParams) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (!value) {
        endpoint = endpoint.replace(`:${key}/`, "");
      } else {
        endpoint = endpoint.replace(`:${key}`, value);
      }
    });
  }
  if (searchParams) {
    endpoint = addQueryStringParams(endpoint, searchParams, true);
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

export const quitEvent = async (eventPk, groupPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getEventEndpoint("quitEvent", { eventPk, groupPk });
  try {
    const response = await axios.delete(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const joinEventAsGroup = async (eventPk, groupPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getEventEndpoint("joinEventAsGroup", { eventPk });
  const body = { groupPk };
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const createEvent = async (data) => {
  const result = {
    data: null,
    errors: null,
  };

  let headers = undefined;
  const url = getEventEndpoint("createEvent");

  try {
    const startTime = DateTime.fromISO(data.startTime)
      .setZone(data.timezone, { keepLocalTime: true })
      .toISO();

    const endTime = DateTime.fromISO(data.endTime)
      .setZone(data.timezone, { keepLocalTime: true })
      .toISO();

    let body = {
      ...data,
      startTime,
      endTime,
      subtype: data.subtype && data.subtype.id,
      organizerGroup: data.organizerGroup && data.organizerGroup.id,
      image: data?.image?.file,
    };

    if (body.image) {
      body = objectToFormData(body);
    }

    const response = await axios.post(url, body, { headers });
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
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
  let body = { ...data };

  if (body.subtype) {
    body.subtype = body.subtype?.id;
  }

  if (body.image || body.compteRenduPhoto) {
    const formData = new FormData();
    Object.keys(body).forEach((e) => {
      if (typeof body[e] !== "undefined") {
        formData.append(e, body[e] || "");
      }
    });
    body = formData;
  }

  try {
    const response = await axios.patch(url, body, { headers });
    result.data = response.data;
  } catch (e) {
    if (e.response && e.response.data) {
      result.error =
        e.response.status === 400 && data.image
          ? { image: "La taille du fichier ne doit pas dépasser 2.5 Mo" }
          : e.response.data;
    } else {
      result.error = e.message;
    }
  }
  return result;
};

export const updateEventProject = async (eventPk, data) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("eventProject", { eventPk });

  try {
    const response = await axios.patch(url, data);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const addEventProjectDocument = async (eventPk, data) => {
  const result = {
    data: null,
    errors: null,
  };
  const url = getEventEndpoint("addEventProjectDocument", { eventPk });
  const body = new FormData();

  Object.keys(data).forEach((e) => {
    body.append(e, data[e]);
  });

  try {
    const response = await axios.post(url, body, { headers });
    result.data = response.data;
  } catch (e) {
    if (!e.response || !e.response.data) {
      result.errors = e.message;
    } else if (e.response.status === 400 && data.file) {
      result.errors = {
        file: "La taille du fichier ne doit pas dépasser le 2.5 Mo",
      };
    } else {
      result.errors = Object.entries(e.response.data).reduce(
        (errors, [field, error]) => ({
          ...errors,
          [field]: Array.isArray(error) ? error[0] : error,
        }),
        {},
      );
    }
  }

  return result;
};

export const getDetailAdvanced = async (eventPk) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("getDetailAdvanced", { eventPk });

  try {
    const response = await axios.patch(url, data);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const addOrganizer = async (eventPk, data) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("addOrganizer", { eventPk });

  try {
    const response = await axios.post(url, data);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const cancelEvent = async (eventPk) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("cancelEvent", { eventPk });

  try {
    const response = await axios.delete(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const getOrganizerGroupSuggestions = async (eventPk, data) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("getOrganizerGroupSuggestions", { eventPk });

  try {
    const response = await axios.get(url, data);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const inviteGroupOrganizer = async (eventPk, data) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("inviteGroupOrganizer", { eventPk });

  try {
    const response = await axios.post(url, data);
    result.data = {
      created: response.status === 201,
      accepted: response.status === 202,
    };
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const getEventMessages = async (eventPk) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("getEventMessages", { eventPk });
  try {
    const response = await axios.patch(url, data);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const getOrganizedEvents = async (params) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("getOrganizedEvents", null, params);

  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};
