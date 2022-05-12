import React from "react";

import theme2022 from "@agir/front/genericComponents/themes/2022";
import themeLFI from "@agir/front/genericComponents/themes/LFI";

const melenchon2022 = {
  type: "2022",
  hasGroupAllocations: false,
  maxAmount: 460000,
  maxAmountWarning: (
    <span>
      Erreur de montant&nbsp;: le maximum du montant total de donation pour une
      personne aux candidats à l'élection présidentielle ne peut pas excéder{" "}
      <strong>4600 €</strong>
    </span>
  ),
  beneficiary: "Mélenchon 2022",
  externalLinkRoute: "melenchon2022",
  title: "Faire un don - Mélenchon 2022",
  theme: theme2022,
  allowedPaymentModes: {
    M: ["system_pay_afcp2022"],
    S: ["system_pay_afcp2022", "check_jlm2022_dons"],
  },
  legalParagraph:
    "Les dons sont destinés à l'AFCP JLM 2022, déclarée à la préfecture de Paris le 15 juin 2021, seule habilitée à recevoir les dons en faveur du candidat Jean-Luc Mélenchon, dans le cadre de la campagne pour l'élection présidentielle de 2022.",
};

const LFI = {
  type: "LFI",
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
    M: ["system_pay"],
    S: ["system_pay", "check_donations"],
  },
  legalParagraph:
    "Les dons seront versés à L'Association de financement de La France insoumise (AFLFI). Premier alinéa de l’article 11-4 de la loi 88-227 du 11 mars 1988 modifiée : une personne physique peut verser un don à un parti ou groupement politique si elle est de nationalité française ou si elle réside en France.",
};

const CONFIG = {
  // 2022: melenchon2022,
  LFI,
  default: LFI,
};

export default CONFIG;
