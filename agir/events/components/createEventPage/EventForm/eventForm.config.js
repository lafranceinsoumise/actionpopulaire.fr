import validate from "@agir/lib/utils/validate";
import { DateTime } from "luxon";

import { COUNTRIES } from "@agir/front/formComponents/CountryField";

let startDate = new Date();
startDate = DateTime.fromJSDate(startDate).plus({ days: 1 });
let endDate = startDate.plus({ hours: 1 });
startDate = new Date(startDate.ts);
endDate = new Date(startDate.ts);

export const DEFAULT_FORM_DATA = {
  name: "",
  organizerGroup: null,
  startTime: startDate.toUTCString(),
  endTime: endDate.toUTCString(),
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  subtype: null,
  onlineUrl: "",
  location: {
    name: "",
    address1: "",
    address2: "",
    city: "",
    zip: "",
    country: COUNTRIES[0].value,
    isDefault: true,
  },
  contact: {
    name: "",
    email: "",
    phone: "",
    hidePhone: false,
    isDefault: true,
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
  timezone: {
    presence: {
      allowEmpty: false,
      message: "Indiquez un fuseau horaire",
    },
  },
  subtype: {
    presence: {
      allowEmpty: false,
      message: "Choisissez un type parmi les options proposées",
    },
  },
  onlineUrl: {
    presence: {
      allowEmpty: true,
    },
    optionalUrl: {
      message: "Indiquez une URL valide",
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
