import axios from "@agir/lib/utils/axios";

const url = "/data-france/communes/chercher/";

const search = async (q, types = []) => {
  if (q.trim().length < 3) {
    return [];
  }

  const params = new URLSearchParams([
    ["q", q],
    ...types.map((t) => ["type", t]),
  ]);

  try {
    const res = await axios.get(url, {
      params,
      headers: { Accept: "application/json" },
    });

    return res.data.results;
  } catch (e) {
    throw new Error("Problème de connexion.");
  }
};

export default search;
