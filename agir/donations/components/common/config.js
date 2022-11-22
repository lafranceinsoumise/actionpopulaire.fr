import React from "react";

import themeLFI from "@agir/front/genericComponents/themes/LFI";

import { MONTHLY_PAYMENT, ONE_TIME_PAYMENT } from "./form.config";

const DONATION = {
  type: "DONATION",
  hasGroupAllocations: true,
  maxAmount: 750000,
  maxAmountWarning: (
    <span>
      Erreur de montant&nbsp;: les dons versés par une personne physique ne
      peuvent excéder <strong>7500 €</strong> par an pour un ou des partis ou
      groupements politiques
    </span>
  ),
  beneficiary: "la France insoumise",
  externalLinkRoute: "lafranceinsoumise",
  title: "Faire un don - La France insoumise",
  theme: themeLFI,
  allowedPaymentModes: {
    [ONE_TIME_PAYMENT]: ["system_pay", "check_donations"],
    // [MONTHLY_PAYMENT]: ["system_pay"],
  },
  legalParagraph:
    "Les dons seront versés à L'Association de financement de La France insoumise (AFLFI). Premier alinéa de l’article 11-4 de la loi 88-227 du 11 mars 1988 modifiée : une personne physique peut verser un don à un parti ou groupement politique si elle est de nationalité française ou si elle réside en France.",
};

const CONFIG = {
  DONATION,
  default: DONATION,
};

export default CONFIG;
