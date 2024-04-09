import large from "./images/illustration_EU24_BG_D.jpg";
import small from "./images/illustration_EU24_BG_M.jpg";
import logo from "@agir/front/genericComponents/logos/FI_eu24.png";

import * as style from "@agir/front/genericComponents/_variables.scss";

const theme = {
  default: style,
  logo,
  logoHeight: "74px",
  progressColor: "#502582",
  primary500: "#502582",
  primary600: "#3E2758",

  illustration: {
    small,
    large,
  },
};

export default theme;
