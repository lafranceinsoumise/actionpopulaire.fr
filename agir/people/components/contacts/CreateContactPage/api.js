import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  validateContact: "/api/contacts/valider/",
  createContact: "/api/contacts/creer/",
};

export const getContactEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const validateContact = async (data) => {
  const result = {
    valid: false,
    errors: null,
  };

  const body = { ...data, group: data?.group?.id || undefined };
  const url = getContactEndpoint("validateContact");

  try {
    await axios.post(url, body);
    result.valid = true;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const createContact = async (data) => {
  const result = {
    data: null,
    errors: null,
  };

  const body = { ...data, group: data?.group?.id || undefined };
  const url = getContactEndpoint("createContact");

  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};
