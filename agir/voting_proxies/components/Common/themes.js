import largeVP from "./images/illustration_voting_proxy_BG_D.png";
import largeVPR from "./images/illustration_voting_proxy_request_BG_D.png";
import smallVP from "./images/illustration_voting_proxy_BG_M.png";
import smallVPR from "./images/illustration_voting_proxy_request_BG_M.png";

import defaultTheme from "@agir/front/genericComponents/themes/legislatives2024";

export const votingProxyTheme = {
  ...defaultTheme,
  illustration: {
    small: smallVP,
    large: largeVP,
  },
};

export const votingProxyRequestTheme = {
  ...defaultTheme,
  illustration: {
    small: smallVPR,
    large: largeVPR,
  },
};
