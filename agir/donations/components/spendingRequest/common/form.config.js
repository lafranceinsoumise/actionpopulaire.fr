import validate from "@agir/lib/utils/validate";

export const TYPE_OPTIONS = {
  IM: {
    value: "IM",
    label: "Impressions",
    icon: "printer",
  },
  CO: {
    value: "CO",
    label: "Achat de consommables (colles, feutres, … )",
    icon: "pen-tool",
  },
  AC: {
    value: "AC",
    label: "Achat de matériel (quincaillerie, matériel de collage, … )",
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
    label: "Location de matériel (mobilier, vaisselle, … )",
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
  },
  O: { value: "O", label: "Autre type de justificatif" },
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
