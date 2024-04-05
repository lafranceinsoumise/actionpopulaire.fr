import largeVP from "./images/illustration_voting_proxy_BG_D.jpg";
import largeVPR from "./images/illustration_voting_proxy_request_BG_D.jpg";
import smallVP from "./images/illustration_voting_proxy_BG_M.jpg";
import smallVPR from "./images/illustration_voting_proxy_request_BG_M.jpg";

import defaultTheme from "@agir/front/genericComponents/themes/eu24";

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
