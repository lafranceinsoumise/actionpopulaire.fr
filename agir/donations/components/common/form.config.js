import validate from "@agir/lib/utils/validate";

export const ONE_TIME_PAYMENT = "S";
export const MONTHLY_PAYMENT = "M";

export const GENDER_OPTIONS = [
  { label: "", value: "" },
  { label: "Madame", value: "F" },
  { label: "Monsieur", value: "M" },
];

export const INITIAL_DATA = {
  email: "",
  firstName: "",
  lastName: "",
  contactPhone: "",
  gender: "",
  locationAddress1: "",
  locationAddress2: "",
  locationCity: "",
  locationCountry: "FR",
  nationality: "FR",
  frenchResident: true,

  to: "",
  paymentMode: "",
  amount: 0,
  paymentTiming: "",
  allocations: [],
  consentCertification: false,
};

export const setFormDataForUser = (user) => (data) => ({
  ...data,
  email: data.email || user.email || INITIAL_DATA.email,
  firstName: data.firstName || user.firstName || INITIAL_DATA.firstName,
  lastName: data.lastName || user.lastName || INITIAL_DATA.lastName,
  contactPhone:
    data.contactPhone || user.contactPhone || INITIAL_DATA.contactPhone,
  locationAddress1:
    data.locationAddress1 || user.address1 || INITIAL_DATA.locationAddress1,
  locationAddress2:
    data.locationAddress2 || user.address2 || INITIAL_DATA.locationAddress2,
  locationZip: data.locationZip || user.zip || INITIAL_DATA.locationZip,
  locationCity: data.locationCity || user.city || INITIAL_DATA.locationCity,
  locationCountry: data.locationCountry || user.country || INITIAL_DATA.country,
  gender: data.gender
    ? data.gender
    : GENDER_OPTIONS.includes(user.gender)
    ? user.gender
    : INITIAL_DATA.gender,
});

export const DONATION_DATA_CONSTRAINTS = {
  email: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
    email: {
      message: "Saisissez une adresse e-mail valide.",
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
      message: "Ce champ ne peut pas être vide.",
    },
    length: {
      maximum: 255,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
  contactPhone: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
    phone: {
      message: "Saisissez un numéro de téléphone valide.",
    },
  },
  gender: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
    inclusion: {
      within: GENDER_OPTIONS.map((option) => option.value).filter(Boolean),
      message: "Veuillez choisir une des options.",
    },
  },
  locationAddress1: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
  },
  locationCity: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
  },
  locationCountry: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
  },
  nationality: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
  },
  frenchResident: {
    inclusion: {
      within: [true],
      message:
        "Si vous n'avez pas la nationalité française, vous devez être résident fiscalement en France pour faire une donation",
    },
  },
  to: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
  },
  paymentMode: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
  },
  amount: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
  },
  paymentTiming: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
  },
  consentCertification: {
    inclusion: {
      within: [true],
      message: "Vous devez cocher la case précédente pour continuer",
    },
  },
};

export const validateDonationData = (data) =>
  validate(data, DONATION_DATA_CONSTRAINTS, {
    format: "cleanMessage",
    fullMessages: false,
  });
