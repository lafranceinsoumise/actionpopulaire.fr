import axios from "@agir/lib/utils/axios";

const ENDPOINT = {
  search: "/api/recherche/",
  searchGroups: "/api/recherche/groupes/",
  searchEvents: "/api/recherche/evenements/",
};

export const getSearch = async (data) => {
  const result = {
    data: null,
    error: null,
  };

  try {
    const response = await axios.get(`${ENDPOINT.search}?q=${data}`);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
