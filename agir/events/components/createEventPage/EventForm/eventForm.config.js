import countries from "localized-countries/data/fr";

import validate from "@agir/lib/utils/validate";

const FIRST_COUNTRY_CODES = ["FR", "PT", "DZ", "MA", "TR", "IT", "GB", "ES"];
const FIRST_COUNTRIES = FIRST_COUNTRY_CODES.map((countryCode) => ({
  value: countryCode,
  label: countries[countryCode],
}));
const OTHER_COUNTRIES = Object.keys(countries)
  .map((countryCode) => {
    if (!FIRST_COUNTRY_CODES.includes(countryCode)) {
      return {
        value: countryCode,
        label: countries[countryCode],
      };
    }
  })
  .filter(Boolean)
  .sort(({ label: label1 }, { label: label2 }) => label1.localeCompare(label2));

export const COUNTRIES = [...FIRST_COUNTRIES, ...OTHER_COUNTRIES];

export const EVENT_DEFAULT_DURATIONS = [
  {
    value: 60,
    label: "1h",
  },
  {
    value: 90,
    label: "1h30",
  },
  {
    value: 120,
    label: "2h",
  },
  {
    value: 180,
    label: "3h",
  },
  {
    value: null,
    label: "Personnalisée",
  },
];

export const DEFAULT_FORM_DATA = {
  name: "",
  organizerGroup: "",
  startTime: new Date().toUTCString(),
  endTime: new Date().toUTCString(),
  subtype: null,
  location: {
    name: "",
    address1: "",
    address2: "",
    city: "",
    zip: "",
    country: "",
  },
  contact: {
    name: "",
    email: "",
    phone: "",
    hidePhone: false,
  },
};

export const FORM_FIELD_CONSTRAINTS = {
  name: {
    presence: {
      allowEmpty: false,
      message: "Donnez un titre à votre événement",
    },
    length: {
      minimum: 3,
      maximum: 100,
      tooShort:
        "Donnez un titre à votre événement d’au moins %{count} caractères",
      tooLong:
        "Le titre de votre événement ne peut pas dépasser les %{count} caractères",
    },
  },
  organizerGroup: {
    presence: {
      allowEmpty: false,
      message: "Indiquez l'organisateur de votre événement",
    },
  },
  startTime: {
    presence: {
      allowEmpty: false,
      message: "Indiquez une date et heure de début",
    },
    datetime: {
      message: "Indiquez une date et heure valides",
    },
  },
  endTime: {
    presence: {
      allowEmpty: false,
      message: "Indiquez une date et heure de fin",
    },
    datetime: {
      message: "Indiquez une date et heure valides",
    },
  },
  subtype: {
    presence: {
      allowEmpty: false,
      message: "Choisissez un type parmi les options proposées",
    },
  },
  "location.name": {
    presence: {
      allowEmpty: false,
      message: "Donnez un nom au lieu où se déroule l’événement",
    },
  },
  "location.address1": {
    presence: {
      allowEmpty: false,
      message: "Indiquez l’adresse du lieu où se déroule l’évément",
    },
  },
  "location.city": {
    presence: {
      allowEmpty: false,
      message: "Indiquez la ville où se déroule l’événement",
    },
  },
  "location.zip": {
    presence: {
      allowEmpty: false,
      message: "Indiquez un code postal",
    },
  },
  "location.country": {
    presence: {
      allowEmpty: false,
      message: "Indiquez le nom du pays où se déroule l’événement",
    },
  },
  "contact.name": {
    presence: {
      allowEmpty: false,
      message:
        "Indiquez le nom de la personne à contacter concernant cet événement",
    },
  },
  "contact.email": {
    presence: {
      allowEmpty: false,
      message:
        "Indiquez une adresse e-mail de contact pour les personnes qui souhaiteraient se renseigner",
    },
    email: {
      message: "Indiquez une adresse e-mail valide",
    },
  },
  "contact.phone": {
    presence: {
      allowEmpty: false,
      message: "Indiquez un numéro de téléphone",
    },
    phone: {
      message: "Indiquez un numéro de téléphone valide",
    },
  },
};

export const validateData = (data) =>
  validate(data, FORM_FIELD_CONSTRAINTS, {
    format: "cleanMessage",
    fullMessages: false,
  });
