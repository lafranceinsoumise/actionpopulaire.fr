import React, { useEffect, useState } from "react";
import { useIsOffline } from "@agir/front/offline/hooks";
import logger from "@agir/lib/utils/logger";
import { animated, useTransition } from "react-spring";
import styled from "styled-components";
import styles from "@agir/front/genericComponents/_variables.scss";
import style from "@agir/front/genericComponents/_variables.scss";

const log = logger(__filename);

const StyledWarning = styled(animated.div)`
  position: fixed;
  top: 72px;
  width: 100%;
  z-index: ${style.zindexTopBar};

  @media (max-width: ${style.collapse}px) {
    top: 56px;
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

const ConnectivityWarning = () => {
  const offline = useIsOffline();
  log.debug(`Offline ${offline}`);

  const [display, setDisplay] = useState(offline);
  log.debug(`Display ${display}`);

  useEffect(() => {
    let timeout = setTimeout(() => setDisplay(offline), offline ? 0 : 5000);
    return () => clearTimeout(timeout);
  }, [offline]);

  let params;
  switch (offline) {
    case false:
      params = [styles.green500, styles.green100, "Connexion rétablie"];
      break;
    case true:
      params = [styles.redNSP, styles.red100, "Aucune connexion internet"];
      break;
    default:
      params = [styles.primary500, styles.primary100, "Connexion en cours..."];
  }

  const transitions = useTransition(display, null, {
    initial: null,
    enter: { height: 30 },
    leave: { height: 0 },
  });

  return transitions.map(
    ({ item, key, props }) =>
      item && (
        <StyledWarning
          key={key}
          style={{
            backgroundColor: params[0],
            color: params[1],
            ...props,
          }}
        >
          <div>{params[2]}</div>
        </StyledWarning>
      )
  );
};

export default ConnectivityWarning;
