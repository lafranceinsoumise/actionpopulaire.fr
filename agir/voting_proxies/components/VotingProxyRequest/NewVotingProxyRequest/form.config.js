import validate from "@agir/lib/utils/validate";

const INITIAL_DATA = {
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
  votingLocation: "",
  pollingStationNumber: "",
  votingDates: [],
};

export const getInitialData = (user) =>
  user
    ? {
        ...INITIAL_DATA,
        email: user.email || "",
        phone: user.contactPhone || "",
      }
    : { ...INITIAL_DATA };

export const VOTING_PROXY_REQUEST_CONSTRAINTS = {
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
  email: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut être vide.",
    },
    email: {
      message: "Saisissez une adresse e-mail valide.",
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
  votingDates: {
    presence: {
      allowEmpty: false,
      message: "Cette sélection ne peut être vide.",
    },
  },
};

export const validateVotingProxyRequest = (data) =>
  validate(data, VOTING_PROXY_REQUEST_CONSTRAINTS, {
    format: "cleanMessage",
    fullMessages: false,
  });
