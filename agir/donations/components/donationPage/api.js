import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  createDonation: "/api/dons/",
  sendDonation: "/api/envoyer-dons/",
};

export const getDonationEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const createDonation = async (body) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getDonationEndpoint("createDonation");
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    if (e.response && e.response.data && Object.keys(e.response.data)[0]) {
      result.error = e.response.data[Object.keys(e.response.data)[0]];
    } else {
      result.error = (e.response && e.response.data) || e.message;
    }
  }

  return result;
};

export const sendDonation = async (data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getDonationEndpoint("sendDonation");

  try {
    const response = await axios.post(url, data);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
