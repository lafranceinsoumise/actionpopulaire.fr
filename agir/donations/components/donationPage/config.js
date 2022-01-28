import React from "react";

import theme2022 from "@agir/front/genericComponents/themes/2022";
import themeLFI from "@agir/front/genericComponents/themes/LFI";

const melenchon2022 = {
  maxAmount: 460000,
  maxAmountWarning: (
    <span>
      Erreur de montant&nbsp;: le maximum du montant total de donation pour une
      personne aux candidats à l'élection présidentielle ne peut pas excéder{" "}
      <strong>4600 €</strong>
    </span>
  ),
  externalLinkRoute: "melenchon2022",
  title: "Faire un don - Mélenchon 2022",
  theme: theme2022,
};

const LFI = {
  maxAmount: 750000,
  maxAmountWarning: (
    <span>
      Erreur de montant&nbsp;: les dons versés par une personne physique ne
      peuvent excéder <strong>7500 €</strong> par an pour un ou des partis ou
      groupements politiques
    </span>
  ),
  externalLinkRoute: "lafranceinsoumise",
  title: "Faire un don - La France insoumise",
  theme: themeLFI,
};

const CONFIG = {
  2022: melenchon2022,
  LFI,
  default: LFI,
};

export default CONFIG;
