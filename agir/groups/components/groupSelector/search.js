import axios from "@agir/lib/utils/axios";

const url = "/groupes/chercher/";

const search = async (terms) => {
  if (terms.trim().length < 3) {
    return [];
  }

  const res = await axios.get(url, {
    params: { q: terms, certified: "Y" },
  });

  return res.data.results;
};

export default search;
