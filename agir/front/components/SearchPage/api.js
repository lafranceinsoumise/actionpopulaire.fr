import axios from "@agir/lib/utils/axios";

const ENDPOINT = {
  search: "/api/recherche/",
};

export const getSearch = async (data) => {
  const result = {
    data: null,
    error: null,
  };

  try {
    const response = await axios.get(ENDPOINT.search, { params: { q: data } });
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
