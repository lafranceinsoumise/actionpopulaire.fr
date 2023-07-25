const NBSP = "\u00A0";

export function displayNumber(n, decimals) {
  if (!decimals) decimals = 0;
  const s = Math.abs(Math.round(n * Math.pow(10, decimals)))
    .toString()
    .padStart(decimals + 1, "0");

  return (
    (n < 0 ? "-" : "") +
    (s.slice(0, s.length - decimals) || "0") +
    (decimals > 0 ? "," + s.slice(s.length - decimals) : "")
  );
}

export function parsePrice(s) {
  const m = s.match(/^([+-]?)([0-9]+)(?:[,.]([0-9]{0,2}))?$/);

  if (m !== null) {
    const newText = m[1] + m[2] + (m[3] || "").padEnd(2, "0").slice(0, 3);
    return parseInt(newText);
  }

  return null;
}

export function displayPrice(n, forceCents = false, unit = "€") {
  let price =
    !forceCents && n % 100 === 0
      ? `${displayNumber(n / 100, 0)}`
      : `${displayNumber(n / 100, 2)}`;

  if (unit) {
    price += `${NBSP}${unit}`;
  }

  return price;
}

export const GENDER = {
  female: "F",
  male: "M",
  other: "O",
};
/**
 * function getGenderedWord
 *
 *
 */
export const getGenderedWord = (
  gender,
  inclusiveWord,
  feminineWord,
  masculineWord
) => {
  if (typeof inclusiveWord !== "string") {
    return "";
  }
  inclusiveWord = inclusiveWord.trim();
  gender = typeof gender === "string" ? gender.toUpperCase() : null;
  if (
    !gender ||
    !Object.values(GENDER).includes(gender) ||
    gender === GENDER.other
  ) {
    return inclusiveWord;
  }
  if (gender === GENDER.female && feminineWord) {
    return feminineWord;
  }
  if (gender == GENDER.male && masculineWord) {
    return masculineWord;
  }
  // Automatic gendering of inclusive word only works for words whose suffix is either "e" or "es"
  const parsedWord = inclusiveWord.match(/^(.+)[⋅|·]{1}(e{1}s?)$/i);
  if (!Array.isArray(parsedWord)) {
    return inclusiveWord;
  }
  let [, root, suffix] = parsedWord;
  const commonPlural =
    suffix.split("").pop().toLowerCase() === "s" &&
    root.split("").pop().toLowerCase() !== "s" &&
    root.split("").pop().toLowerCase() !== "x"
      ? suffix.split("").pop()
      : "";
  suffix = commonPlural ? suffix.slice(0, -1) : suffix;
  const commonRootLength = commonPlural
    ? root.length - suffix.length + 1
    : root.length;

  return gender === GENDER.female
    ? `${root.slice(0, commonRootLength)}${suffix}${commonPlural}`
    : `${root}${commonPlural}`;
};

const COMMUNE_ARTICLES = {
  "de ": "à ",
  "d'": "à ",
  "du ": "au ",
  "de la ": "à la ",
  "des ": "aux ",
  "de l'": "à l'",
  "de las ": "à las ",
  "de los ": "à los ",
};

export const communeNameOfToIn = (nameOf) =>
  Object.entries(COMMUNE_ARTICLES).reduce(
    (string, [key, value]) => string.replace(new RegExp("^" + key, "i"), value),
    nameOf
  );
