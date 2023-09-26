import validate from "@agir/lib/utils/validate";

export const TIMING_OPTIONS = {
  P: {
    value: "P",
    label: "Il s’agit d’un remboursement  (dépense passée)",
    shortLabel: "Passée",
  },
  U: {
    value: "U",
    label: "Il s’agit d’une demande d’achat (dépense future)",
    shortLabel: "Future",
  },
};

export const CATEGORY_OPTIONS = {
  IM: {
    value: "IM",
    label: "Impressions",
    icon: "printer",
  },
  CO: {
    value: "CO",
    label: "Achat de consommables (colles, feutres, etc.)",
    icon: "pen-tool",
  },
  AC: {
    value: "AC",
    label: "Achat de matériel (quincaillerie, matériel de collage, etc.)",
    icon: "package",
  },
  DE: {
    value: "DE",
    label: "Déplacement",
    icon: "map",
  },
  HE: {
    value: "HE",
    label: "Hébergement",
    icon: "home",
  },
  SA: {
    value: "SA",
    label: "Location de salle",
    icon: "map-pin",
  },
  MA: {
    value: "MA",
    label: "Location de matériel (mobilier, vaisselle, etc.)",
    icon: "shopping-bag",
  },
  TE: {
    value: "TE",
    label: "Location de matériel technique (sono, vidéo)",
    icon: "video",
  },
  VE: {
    value: "VE",
    label: "Location de véhicule",
    icon: "truck",
  },
};

export const DOCUMENT_TYPE_OPTIONS = {
  E: { value: "E", label: "Devis" },
  I: { value: "I", label: "Facture" },
  B: { value: "B", label: "Impression" },
  P: {
    value: "P",
    label: "Photo ou illustration de l'événement, de la salle, du matériel",
    smallLabel: "Photo / illustration",
  },
  O: { value: "O", label: "Autre type de justificatif", smallLabel: "Autre" },
};

const INITIAL_DATA = {
  title: "",
  campaign: false,
  spendingDate: null,
  attachments: [],
};

export const getInitialData = (user, group) => ({
  ...INITIAL_DATA,
  group,
  contact: {
    ...INITIAL_DATA.contact,
    name: user?.displayName || "",
    phone: user?.contactPhone || "",
  },
});

export const getInitialDataFromSpendingRequest = (spendingRequest) => ({
  title: spendingRequest.title || "",
  timing: spendingRequest.timing,
  campaign: spendingRequest.campaign || false,
  amount: spendingRequest.amount,
  group: spendingRequest.group.id,
  category: spendingRequest.category,
  explanation: spendingRequest.explanation,
  event: spendingRequest.event,
  spendingDate: spendingRequest.spendingDate || null,
  contact: spendingRequest.contact,
  bankAccount: spendingRequest.bankAccount,
});

export const SPENDING_REQUEST_DRAFT_CONSTRAINT = {
  title: {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
    length: {
      maximum: 200,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
  category: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
    inclusion: {
      within: Object.values(CATEGORY_OPTIONS)
        .map((option) => option.value)
        .filter(Boolean),
      message: "Veuillez choisir une des options.",
    },
  },
};

export const SPENDING_REQUEST_VALIDATION_CONSTRAINT = {
  ...SPENDING_REQUEST_DRAFT_CONSTRAINT,
  explanation: {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
    length: {
      maximum: 1500,
      tooLong:
        "La valeur de ce champ ne peut pas dépasser les %{count} caractères",
    },
  },
  spendingDate: {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
    datetime: {
      message: "Saisissez une date valide",
    },
  },
  "contact.name": {
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
  "contact.phone": {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
    phone: {
      message: "Saisissez un numéro de téléphone valide.",
    },
  },
  attachments: {
    presence: {
      allowEmpty: false,
      message:
        "Veuillez joindre au moins une pièce justificative à votre demande avant de pouvoir la valider",
    },
  },
  amount: {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
    numericality: {
      greaterThan: 0,
      notValid: "Le montant devrait être un nombre supérieur à 0",
      notGreaterThan: "Le montant devrait être un nombre supérieur à 0",
    },
  },
  "bankAccount.name": {
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
  "bankAccount.iban": {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
  },
  "bankAccount.bic": {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
  },
  "bankAccount.rib": {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
  },
};

export const DOCUMENT_CONSTRAINT = {
  type: {
    presence: {
      allowEmpty: false,
      message: "Ce champ ne peut pas être vide.",
    },
    inclusion: {
      within: Object.values(DOCUMENT_TYPE_OPTIONS)
        .map((option) => option.value)
        .filter(Boolean),
      message: "Veuillez choisir une des options.",
    },
  },
  title: {
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
  file: {
    presence: {
      allowEmpty: false,
      message: "Ce champ est obligatoire",
    },
  },
};

export const validateSpendingRequestDocument = (data) =>
  validate(data, DOCUMENT_CONSTRAINT, {
    format: "cleanMessage",
    fullMessages: false,
  });

export const validateSpendingRequest = (
  data,
  shouldValidate,
  hasAttachments = true,
) => {
  const constraints = shouldValidate
    ? { ...SPENDING_REQUEST_VALIDATION_CONSTRAINT }
    : { ...SPENDING_REQUEST_DRAFT_CONSTRAINT };

  if (!hasAttachments) {
    constraints.attachments = false;
  }

  const result = validate(data, constraints, {
    format: "cleanMessage",
    fullMessages: false,
  });

  if (hasAttachments && data.attachments) {
    const attachments = data.attachments
      .map(validateSpendingRequestDocument)
      .filter(Boolean);

    if (attachments.length > 0) {
      result.attachments = attachments;
    }
  }

  return result;
};
