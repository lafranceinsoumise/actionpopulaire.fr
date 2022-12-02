import React from "react";

import themeLFI from "@agir/front/genericComponents/themes/LFI";

import { MONTHLY_PAYMENT, SINGLE_TIME_PAYMENT } from "./form.config";

const don = {
  type: "don",
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
    [SINGLE_TIME_PAYMENT]: ["system_pay", "check_donations"],
  },
  legalParagraph:
    "Les dons seront versés à L'Association de financement de La France insoumise (AFLFI). Premier alinéa de l’article 11-4 de la loi 88-227 du 11 mars 1988 modifiée : une personne physique peut verser un don à un parti ou groupement politique si elle est de nationalité française ou si elle réside en France.",
};

const contribution = {
  ...don,
  // Contribution ends in december :
  // - of the current year until august
  // - of the next year from september on
  getEndDate: () =>
    new Date(
      `${
        new Date().getMonth() < 8
          ? new Date().getFullYear()
          : new Date().getFullYear() + 1
      }-12-31 23:59:59`
    ).toISOString(),
  type: "contribution",
  title: "Devenir financeur·euse de La France insoumise",
  fixedRatio: 0.2,
  allowedPaymentModes: {
    [MONTHLY_PAYMENT]: ["system_pay", "check_donations"],
  },
};

const CONFIG = {
  don,
  contribution,
  default: don,
};

export default CONFIG;
