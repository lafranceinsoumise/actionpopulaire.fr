import illustrationLFIBGD from "./images/illustration_FI_BG_D.jpg";
import illustrationLFIBGM from "./images/illustration_FI_BG_M.jpg";

import Logo from "@agir/front/genericComponents/LogoFI";

import * as light from "@agir/front/genericComponents/_variables-light.scss";
import * as dark from "@agir/front/genericComponents/_variables-dark.scss";

const theme = {
  light: {
    secondary600: light.LFIsecondary600,
    secondary500: light.LFIsecondary500,
    secondary150: light.LFIsecondary150,
    secondary100: light.LFIsecondary100,

    primary600: light.LFIprimary600,
    primary500: light.LFIprimary500,
    primary150: light.LFIprimary150,
    primary100: light.LFIprimary100,

    Logo,
    logoHeight: "5rem",
    illustration: {
      small: illustrationLFIBGM,
      large: illustrationLFIBGD,
    },
  },

  dark: {
    secondary600: dark.LFIsecondary600,
    secondary500: dark.LFIsecondary500,
    secondary150: dark.LFIsecondary150,
    secondary100: dark.LFIsecondary100,

    primary600: dark.LFIprimary600,
    primary500: dark.LFIprimary500,
    primary150: dark.LFIprimary150,
    primary100: dark.LFIprimary100,

    Logo,
    logoHeight: "80px",
    illustration: {
      small: illustrationLFIBGM,
      large: illustrationLFIBGD,
    },
  },
};

export default theme;
