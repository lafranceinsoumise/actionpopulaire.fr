import validate from "@agir/lib/utils/validate";

const INITIAL_DATA = {
  votingLocation: "",
  pollingStationNumber: "",
  votingDates: [],
  firstName: "",
  lastName: "",
  dateOfBirth: "",
  phone: "",
  email: "",
  remarks: "",
  address: "",
  zip: "",
  city: "",
  voterId: "",
};

export const getInitialData = (user) =>
  user
    ? {
        ...INITIAL_DATA,
        email: user.email || "",
        phone: user.contactPhone || "",
        dateOfBirth: user.dateOfBirth || "",
        address: user.address1 || "",
        zip: user.zip || "",
        city: user.city || "",
      }
    : { ...INITIAL_DATA };

export const VOTING_PROXY_CONSTRAINTS = {
  votingLocation: {
    presence: {
      allowEmpty: false,
      message: "Cette sélection ne peut être vide.",
    },
  },
  pollingStationNumber: {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
    length: {
      maximum: 255,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
  voterId: {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
    length: {
      maximum: 255,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
  votingDates: {
    presence: {
      allowEmpty: false,
      message: "Cette sélection ne peut être vide.",
    },
  },
  firstName: {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
    length: {
      maximum: 255,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
  lastName: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut être vide.",
    },
    length: {
      maximum: 255,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
  dateOfBirth: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut être vide.",
    },
    date: {
      message: "Indiquez une date valide",
    },
  },
  phone: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut être vide.",
    },
    phone: {
      message: "Saisissez un numéro de téléphone valide.",
    },
  },
  email: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut être vide.",
    },
    email: {
      message: "Saisissez une adresse e-mail valide.",
    },
  },
  remarks: {
    presence: {
      allowEmpty: true,
    },
    length: {
      maximum: 255,
      tooLong: "Assurez-vous que ce champ comporte au plus 255 caractères.",
    },
  },
};

const FRANCE_VOTING_PROXY_CONSTRAINTS = {
  ...VOTING_PROXY_CONSTRAINTS,
  address: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut être vide.",
    },
    length: {
      maximum: 255,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
  zip: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut être vide.",
    },
    length: {
      maximum: 20,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
  city: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut être vide.",
    },
    length: {
      maximum: 255,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
};

export const validateVotingProxy = (data, isAbroad = false) =>
  validate(
    data,
    isAbroad ? VOTING_PROXY_CONSTRAINTS : FRANCE_VOTING_PROXY_CONSTRAINTS,
    {
      format: "cleanMessage",
      fullMessages: false,
    },
  );
