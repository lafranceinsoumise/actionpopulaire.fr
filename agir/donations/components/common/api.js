import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  createDonation: "/api/dons/",
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

export const createDonation = async (data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getDonationEndpoint("createDonation");

  try {
    const response = await axios.post(url, data);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
