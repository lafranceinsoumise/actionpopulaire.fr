import axios from "@agir/lib/utils/axios";
import { DateTime } from "luxon";

export const ENDPOINT = {
  getEvent: "/api/evenements/:eventPk/",
  rsvpEvent: "/api/evenements/:eventPk/inscription/",
  quitEvent: "/api/evenements/:eventPk/inscription/",
  eventPropertyOptions: "/api/evenements/options/",
  createEvent: "/api/evenements/creer/",
  updateEvent: "/api/evenements/:eventPk/modifier/",
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

export const createEvent = async (data) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("createEvent");

  try {
    const startTime = DateTime.fromISO(data.startTime)
      .setZone(data.timezone, { keepLocalTime: true })
      .toISO();

    const endTime = DateTime.fromISO(data.endTime)
      .setZone(data.timezone, { keepLocalTime: true })
      .toISO();

    const body = {
      ...data,
      startTime,
      endTime,
      subtype: data.subtype && data.subtype.id,
      organizerGroup: data.organizerGroup && data.organizerGroup.id,
    };

    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const updateEvent = async (eventPk, data) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getEventEndpoint("updateEvent", { eventPk });

  try {
    const response = await axios.patch(url, data);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};
