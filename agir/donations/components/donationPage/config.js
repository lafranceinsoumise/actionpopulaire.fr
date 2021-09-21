import style from "@agir/front/genericComponents/_variables.scss";

import logoJLM2022 from "@agir/front/genericComponents/logos/melenchon2022.svg";
import logoLFI from "@agir/front/genericComponents/logos/lfi.svg";

import don2022BGD from "./images/Don_2022_BG_D.jpg";
import don2022BGM from "./images/Don_2022_BG_M.jpg";
import donLFIBGD from "./images/Don_FI_BG_D.jpg";
import donLFIBGM from "./images/Don_FI_BG_M.jpg";

const melenchon2022 = {
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
  melenchon2022,
  LFI,
  default: LFI,
};

export default CONFIG;
