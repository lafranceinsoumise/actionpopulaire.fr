import { DateTime } from "luxon";

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

export const parseDiscountCodes = (discountCodes) => {
  if (!Array.isArray(discountCodes)) {
    return null;
  }

  return discountCodes.map((code) => {
    const expirationDateTime = DateTime.fromJSDate(
      new Date(code.expirationDate)
    );
    let expiration = expirationDateTime.diffNow("days").days;
    expiration =
      typeof expiration === "number" ? `${Math.ceil(expiration)} jours` : "";

    return {
      ...code,
      expiration,
      date: expirationDateTime.setLocale("fr-FR").toFormat("dd MMMM yyyy"),
    };
  });
};
