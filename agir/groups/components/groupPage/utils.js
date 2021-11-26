import { DateTime } from "luxon";

import { communeNameOfToIn } from "@agir/lib/utils/display";

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
  return `${type} ${communeNameOfToIn(nameOf)} (${zip})`;
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
