import React from "react";
import style from "@agir/front/genericComponents/_variables.scss";

import logoJLM2022 from "@agir/front/genericComponents/logos/melenchon2022.svg";
import logoLFI from "@agir/front/genericComponents/logos/lfi.svg";

import don2022BGD from "./images/Don_2022_BG_D.jpg";
import don2022BGM from "./images/Don_2022_BG_M.jpg";
import donLFIBGD from "./images/Don_FI_BG_D.jpg";
import donLFIBGM from "./images/Don_FI_BG_M.jpg";

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
  theme: {
    default: style,
    logo: logoJLM2022,
    logoHeight: "35px",
    illustration: {
      small: don2022BGM,
      large: don2022BGD,
    },
    secondary600: "#E50B2D",
    secondary500: "#F53B3B",
    secondary150: "#F2C2C8",
    secondary100: "#FCEBEB",

    primary600: "#250776",
    primary500: "#3F2682",
    primary150: "#CEC4EB",
    primary100: "#E9E1FF",
  },
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
  theme: {
    default: style,
    logo: logoLFI,
    logoHeight: "70px",
    illustration: {
      small: donLFIBGM,
      large: donLFIBGD,
    },
    secondary600: "#B71F00",
    secondary500: "#C9462C",
    secondary150: "#F2CAC2",
    secondary100: "#FDECEE",

    primary600: "#07758A",
    primary500: "#0098B6",
    primary150: "#B1D8E3",
    primary100: "#D8EEF8",
  },
};

const CONFIG = {
  2022: melenchon2022,
  LFI,
  default: LFI,
};

export default CONFIG;
