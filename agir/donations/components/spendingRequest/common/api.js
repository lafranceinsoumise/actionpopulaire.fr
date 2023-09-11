import axios from "@agir/lib/utils/axios";
import { objectToFormData } from "@agir/lib/utils/forms";
import { addQueryStringParams } from "@agir/lib/utils/url";

export const ENDPOINT = {
  createSpendingRequest: "/api/financement/demande/",
  getSpendingRequest: "/api/financement/demande/:spendingRequestPk/",
  updateSpendingRequest: "/api/financement/demande/:spendingRequestPk/",
  deleteSpendingRequest: "/api/financement/demande/:spendingRequestPk/",
  validateSpendingRequest:
    "/api/financement/demande/:spendingRequestPk/valider/",
  createDocument: "/api/financement/demande/:spendingRequestPk/document/",
  retrieveDocument: "/api/financement/document/:documentPk/",
  updateDocument: "/api/financement/document/:documentPk/",
  deleteDocument: "/api/financement/document/:documentPk/",
};

export const getSpendingRequestEndpoint = (key, params, searchParams) => {
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

export const createSpendingRequestOptions = async () => {
  const result = {
    data: null,
    error: null,
  };

  const url = getSpendingRequestEndpoint("createSpendingRequest");

  try {
    const response = await axios.options(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

const formatSpendingRequestData = (data, validate = false) => {
  const fData = { ...data, shouldValidate: !!validate };
  // Send groupId instead of group object
  fData.groupId = (fData.group && fData.group.id) || null;
  delete fData.group;

  // Send eventId instead of event object
  fData.eventId = (fData.event && fData.event.id) || null;
  delete fData.event;

  // Unchanged bankAccount.rib is a string and can be safely removed
  if (typeof data.bankAccount.rib === "string") {
    delete fData.bankAccount.rib;
  }

  return fData;
};

export const createSpendingRequest = async (data, validate) => {
  const result = {
    data: null,
    error: null,
  };

  const url = getSpendingRequestEndpoint("createSpendingRequest");

  const body = objectToFormData(formatSpendingRequestData(data, validate));

  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateSpendingRequest = async (
  spendingRequestPk,
  data,
  validate,
) => {
  const result = {
    data: null,
    error: null,
  };

  const url = getSpendingRequestEndpoint("updateSpendingRequest", {
    spendingRequestPk,
  });

  const body = objectToFormData(formatSpendingRequestData(data, validate));

  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || { global: e.message };
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
    if (!e.response) {
      result.error = e.message || "Une erreur est survenue";
    } else {
      switch (e.response.status) {
        case 403:
          result.error = "Cette demande ne peut pas être supprimée";
          break;
        case 404:
          result.error = "La demande n'a pas pu être retrouvée";
          break;
        default:
          result.error = e.response.data || "Une erreur est survenue";
      }
    }
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

export const createDocument = async (spendingRequestPk, data) => {
  const result = {
    data: null,
    error: null,
  };

  const url = getSpendingRequestEndpoint("createDocument", {
    spendingRequestPk,
  });

  const body = objectToFormData({ ...data, request: spendingRequestPk });

  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateDocument = async (documentPk, data) => {
  const result = {
    data: null,
    error: null,
  };

  const url = getSpendingRequestEndpoint("updateDocument", { documentPk });
  const body =
    typeof data.file === "string"
      ? { ...data, file: undefined }
      : objectToFormData(data);

  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || { global: e.message };
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
