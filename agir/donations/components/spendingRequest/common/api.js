import axios from "@agir/lib/utils/axios";
import { objectToFormData } from "@agir/lib/utils/forms";

export const ENDPOINT = {
  createSpendingRequest: "/api/financement/demande/",
  getSpendingRequest: "/api/financement/demande/:spendingRequestPk/",
  updateSpendingRequest: "/api/financement/demande/:spendingRequestPk/",
  deleteSpendingRequest: "/api/financement/demande/:spendingRequestPk/",
  validateSpendingRequest:
    "/api/financement/demande/:spendingRequestPk/valider/",
  retrieveDocument: "/api/financement/document/:documentPk/",
  updateDocument: "/api/financement/document/:documentPk/",
  deleteDocument: "/api/financement/document/:documentPk/",
};

export const getSpendingRequestEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const createSpendingRequest = async (data) => {
  const result = {
    data: null,
    error: null,
  };

  const url = getSpendingRequestEndpoint("createSpendingRequest");
  const body = objectToFormData(data);

  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateSpendingRequest = async (spendingRequestPk, data) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getSpendingRequestEndpoint("updateSpendingRequest", {
    spendingRequestPk,
  });
  const body = objectToFormData(data);

  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const deleteSpendingRequest = async (spendingRequestPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getSpendingRequestEndpoint("deleteSpendingRequest", {
    spendingRequestPk,
  });
  try {
    const response = await axios.delete(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const validateSpendingRequest = async (spendingRequestPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getSpendingRequestEndpoint("validateSpendingRequest", {
    spendingRequestPk,
  });
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateDocument = async (documentPk, data) => {
  const result = {
    data: null,
    errors: null,
  };

  const url = getSpendingRequestEndpoint("updateDocument", { documentPk });
  const body = objectToFormData(data);

  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const deleteDocument = async (documentPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getSpendingRequestEndpoint("deleteDocument", { documentPk });
  try {
    const response = await axios.delete(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
