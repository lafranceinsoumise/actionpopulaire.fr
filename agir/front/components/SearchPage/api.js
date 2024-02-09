import axios from "@agir/lib/utils/axios";

const ENDPOINT = {
  search: "/api/recherche/",
};

export const getSearch = async ({ search, type, filters }) => {
  const result = {
    data: null,
    error: null,
  };

  const filterParams = {};
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      filterParams[key] = typeof value === "object" ? value?.value : value;
    }
  });

  try {
    const response = await axios.get(ENDPOINT.search, {
      params: { q: search, type, filters: filterParams },
    });
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
