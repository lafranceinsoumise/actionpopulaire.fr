import axios from "@agir/lib/utils/axios";

const search = async terms => {
  if (terms.trim().length < 3) {
    return [];
  }

  const res = await axios.get("/groupes/chercher", {
    params: { q: terms, certified: "Y" }
  });

  return res.data.results.map(({ id, name, location_zip }) => ({
    id,
    name: `${name} (${location_zip})`
  }));
};

export default search;
