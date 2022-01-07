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
};

export const getInitialData = (user) =>
  user
    ? {
        ...INITIAL_DATA,
        email: user.email || "",
        phone: user.contactPhone || "",
        dateOfBirth: user.dateOfBirth || "",
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
      message: "Ce champ ne peut être vide.",
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
};

export const validateVotingProxy = (data) =>
  validate(data, VOTING_PROXY_CONSTRAINTS, {
    format: "cleanMessage",
    fullMessages: false,
  });
