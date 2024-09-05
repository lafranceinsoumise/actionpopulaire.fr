import React, { useEffect, useMemo, useState } from "react";
import { animated, useTransition } from "@react-spring/web";
import styled from "styled-components";

import { useIsOffline } from "@agir/front/offline/hooks";
import { useDownloadBanner } from "@agir/front/app/hooks.js";
import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

const StyledWarning = styled(animated.div)`
  position: fixed;
  top: ${({ $hasTopBar }) => ($hasTopBar ? "72px" : "0")};
  width: 100%;
  z-index: ${(props) => props.theme.zindexTopBar};
  color: ${(props) => props.theme[props.color]};
  background: ${(props) => props.theme[props.backgroundCOlor]};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    top: ${({ $hasTopBar, $hasDownloadBanner }) => {
      if ($hasTopBar && $hasDownloadBanner) {
        return "136px";
      }
      if ($hasTopBar) {
        return "56px";
      }
      return "0";
    }};
  }

  & > div {
    overflow: hidden;
    text-transform: uppercase;
    font-weight: 600;
    text-align: center;
    font-size: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }
`;

const ConnectivityWarning = ({ hasTopBar }) => {
  const [hasDownloadBanner] = useDownloadBanner();
  const offline = useIsOffline();
  log.debug(`Offline ${offline}`);
  const [display, setDisplay] = useState(offline);
  log.debug(`Display ${display}`);

  const [backgroundColor, color, warning] = useMemo(() => {
    switch (offline) {
      case false:
        return ["success500", "success100", "Connexion rétablie"];
      case true:
        return ["error500", "error100", "Aucune connexion internet"];
      default:
        return ["primary500", "primary100", "Connexion en cours..."];
    }
  }, [offline]);

  useEffect(() => {
    let timeout = setTimeout(() => setDisplay(!!offline), offline ? 0 : 5000);
    return () => clearTimeout(timeout);
  }, [offline]);

  const transitions = useTransition(display, {
    initial: null,
    enter: { height: 30 },
    leave: { height: 0 },
  });

  return transitions(
    (style, item) =>
      item && (
        <StyledWarning
          color
          backgroundColor
          style={style}
          $hasTopBar={hasTopBar}
          $hasDownloadBanner={hasDownloadBanner}
        >
          <div>{warning}</div>
        </StyledWarning>
      ),
  );
};

export default ConnectivityWarning;
