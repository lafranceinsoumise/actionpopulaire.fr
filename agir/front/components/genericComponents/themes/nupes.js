import illustration2022BGD from "./images/illustration_2022_BG_D.jpg";
import illustration2022BGM from "./images/illustration_2022_BG_M.jpg";

import logo from "@agir/front/genericComponents/logos/nupes-2l.png";

import * as style from "@agir/front/genericComponents/_variables.scss";

const theme = {
  default: style,
  logo,
  logoHeight: "80px",
  secondary600: "#E50B2D",
  secondary500: "#F53B3B",
  secondary150: "#F2C2C8",
  secondary100: "#FCEBEB",
  primary600: "#250776",
  primary500: "#3F2682",
  primary150: "#CEC4EB",
  primary100: "#E9E1FF",
  progressColor: style.nupesBlue,

  illustration: {
    small: illustration2022BGM,
    large: illustration2022BGD,
  },
};

export default theme;
