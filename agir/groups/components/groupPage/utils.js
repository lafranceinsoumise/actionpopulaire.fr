const ARTICLES = {
  "de ": "à ",
  "d'": "à ",
  "du ": "au ",
  "de la ": "à la ",
  "des ": "aux ",
  "de l'": "à l'",
  "de las ": "à las ",
  "de los ": "à los ",
};

export const getGroupTypeWithLocation = (type, location, commune) => {
  const { city, zip } = location || {};
  const { nameOf } = commune || {};
  if (!zip) {
    return type;
  }
  if (!city && !nameOf) {
    return `${type} (${zip})`;
  }
  if (!nameOf) {
    return `${type} à ${city} (${zip})`;
  }
  const city_part = Object.entries(ARTICLES).reduce(
    (string, [key, value]) => string.replace(new RegExp("^" + key, "i"), value),
    nameOf
  );
  return `${type} ${city_part} (${zip})`;
};
