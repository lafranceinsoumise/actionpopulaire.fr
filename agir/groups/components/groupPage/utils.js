import { DateTime } from "luxon";

import { communeNameOfToIn } from "@agir/lib/utils/display";

export const getGroupTypeWithLocation = (type, location) => {
  const { city, zip, commune } = location || {};
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
  const codes = [];
  const specialCodes = [];

  if (!Array.isArray(discountCodes)) {
    return [codes, specialCodes];
  }

  discountCodes.forEach((code) => {
    const expirationDateTime = DateTime.fromJSDate(new Date(code.expiration));

    const expirationMonthStart = expirationDateTime.startOf("month");

    let expiration = expirationMonthStart.diffNow("days").days;
    expiration =
      typeof expiration === "number" ? `${Math.ceil(expiration)} jours` : "";

    const isEarly = expirationMonthStart.diffNow("months").months > 1;
    const parsedCode = {
      ...code,
      expiration,
      month: expirationDateTime
        .minus({ months: 1 })
        .setLocale("fr-FR")
        .toFormat("LLLL")
        .toLowerCase(),
      date: expirationMonthStart.setLocale("fr-FR").toFormat("dd MMMM yyyy"),
      dateExact: expirationDateTime
        .minus({ day: 1 })
        .setLocale("fr-FR")
        .toFormat("dd MMMM yyyy"),
      isEarly,
    };

    code.label ? specialCodes.push(parsedCode) : codes.push(parsedCode);
  });

  return [codes, specialCodes];
};
