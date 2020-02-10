/***
 * Formate la valeur transmise au format IBAN en préservant la position logique du curseur.
 *
 * Le format employé est le format classique utilisé pour les IBAN : un espace tous les 4 caractères.
 * @param value: number la valeur telle que saisie
 * @param cursor: string la position actuelle du curseur
 * @param deleteBackwards: boolean l'utilisateur vient-il d'effacer avec la touche backspace ?
 * @returns {{cursor: number, value: string}}
 */
export function formatInputContent(value, cursor, deleteBackwards = false) {
  const beforeCursor = value
    .slice(0, cursor)
    .toUpperCase()
    .replace(/[^A-Z0-9]+/g, "");
  const afterCursor = value
    .slice(cursor)
    .toUpperCase()
    .replace(/[^A-Z0-9]+/g, "");

  if (beforeCursor === "" && afterCursor === "") {
    return { value: "", cursor: 0 };
  }

  const spacelessCursor = beforeCursor.length;

  const formatedValue = (beforeCursor + afterCursor).match(/.{1,4}/g).join(" ");

  let formatedCursor = spacelessCursor + Math.floor(spacelessCursor / 4);
  if (spacelessCursor % 4 === 0 && deleteBackwards) {
    formatedCursor--;
  }

  return {
    value: formatedValue,
    cursor: Math.min(formatedCursor, formatedValue.length)
  };
}

/**
 * Convertit les lettres d'un IBAN en une chaîne de caractères de 2 chiffres
 * selon la convention de calcul de la somme de contrôle des IBAN:
 *  A:"10", B:"11", C:"12" ... (Les chiffres ne sont pas affectés).
 * @param {string} iban - L'IBAN à traiter
 * @returns {string} - L'IBAN avec les lettres remplacées.
 */
function convertIBANLetters(iban) {
  return iban.replace(/[A-Z]/g, c => parseInt(c, 36).toString());
}

/**
 * Applique l'operation modulo sur un nombre contenue dans un tableau.
 * @param {Array.<number>} arrNbr - Un tableau contenant les différentes partie du nombre.
 * L'index 0 représente la plus petite partie (Little endian style)
 * @param {number} tenPower - Le nombre de chiffre par case du tableau
 * @param {number} mod - the
 * @returns {number}
 */
export function arrayNumberModulo(arrNbr, tenPower, mod) {
  let rest = 0;
  const base = Math.pow(10, tenPower);

  for (let i = arrNbr.length - 1; i >= 0; i--) {
    rest = (base * rest + arrNbr[i]) % mod;
  }
  return rest;
}

/**
 *  Convertie une chaîne de caractère en un tableau contenant les différentes partie du nombre.
 * L'index 0 représente la plus petite partie (Little endian)
 * @param {String} strNbr - Une chaîne de caractère qui décrit le nombre
 * @param {number} tenPower - Le nombre de digit par case du tableau.
 * @returns {Array.<number>} - Le tableau décrivant le nombre.
 */
export function strToArrayNumber(strNbr, tenPower) {
  let arrayNbr = [];
  const max = Math.ceil(strNbr.length / tenPower);

  for (let i = 0, id_char = strNbr.length; i < max; i++, id_char -= tenPower) {
    const first = Math.max(id_char - tenPower, 0);
    arrayNbr[i] = first !== id_char ? strNbr.slice(first, id_char) : "0";
    arrayNbr[i] = parseInt(arrayNbr[i]);
  }
  return arrayNbr;
}

export function isIBANValid(iban) {
  const tenPower = 8;
  const rawValue = iban.toUpperCase().replace(/[^A-Z0-9]+/g, "");
  const value = rawValue.slice(4, rawValue.length) + rawValue.slice(0, 4);
  const ibanTab = strToArrayNumber(convertIBANLetters(value), tenPower);
  const remainder = arrayNumberModulo(ibanTab, tenPower, 97);
  return remainder === 1;
}
