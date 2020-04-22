import axios from "axios";

const url = "/data-france/communes/";

const search = async q => {
  if (q.trim().length < 3) {
    return [];
  }

  try {
    const res = await axios.get(url, {
      params: { q },
      headers: { Accept: "application/json" }
    });

    return res.data.results;
  } catch (e) {
    throw new Error("Problème de connexion.");
  }
};

export default search;
