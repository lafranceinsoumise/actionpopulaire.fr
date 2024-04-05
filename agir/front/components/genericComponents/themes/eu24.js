import large from "./images/illustration_EU24_BG_D.jpg";
import small from "./images/illustration_EU24_BG_M.jpg";
import logo from "@agir/front/genericComponents/logos/FI.svg";

import * as style from "@agir/front/genericComponents/_variables.scss";

const theme = {
  default: style,
  logo,
  logoHeight: "74px",
  progressColor: style.primary500,

  illustration: {
    small,
    large,
  },
};

export default theme;
