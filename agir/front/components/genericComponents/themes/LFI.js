import illustrationLFIBGD from "./images/illustration_FI_BG_D.jpg";
import illustrationLFIBGM from "./images/illustration_FI_BG_M.jpg";
import logo from "@agir/front/genericComponents/logos/LFI-NUPES-Violet-H.webp";
import style from "@agir/front/genericComponents/_variables.scss";

const theme = {
  default: style,
  logo,
  logoHeight: "80px",

  secondary600: "#B71F00",
  secondary500: "#C9462C",
  secondary150: "#F2CAC2",
  secondary100: "#FDECEE",
  primary600: "#07758A",
  primary500: "#0098B6",
  primary150: "#B1D8E3",
  primary100: "#D8EEF8",

  illustration: {
    small: illustrationLFIBGM,
    large: illustrationLFIBGD,
  },
};

export default theme;
