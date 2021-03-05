import React, { useEffect, useMemo, useState } from "react";
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

  const [backgroundColor, color, warning] = useMemo(() => {
    switch (offline) {
      case false:
        return [styles.green500, styles.green100, "Connexion rétablie"];
      case true:
        return [styles.redNSP, styles.red100, "Aucune connexion internet"];
      default:
        return [styles.primary500, styles.primary100, "Connexion en cours..."];
    }
  }, [offline]);

  useEffect(() => {
    let timeout = setTimeout(() => setDisplay(!!offline), offline ? 0 : 5000);
    return () => clearTimeout(timeout);
  }, [offline]);

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
            ...props,
            backgroundColor,
            color,
          }}
        >
          <div>{warning}</div>
        </StyledWarning>
      )
  );
};

export default ConnectivityWarning;
