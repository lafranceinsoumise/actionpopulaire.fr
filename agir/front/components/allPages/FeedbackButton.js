import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useTransition, animated } from "@react-spring/web";
import { useEffectOnce } from "react-use";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser, getRoutes } from "@agir/front/globalContext/reducers";
import { useMobileApp } from "@agir/front/app/hooks";
import { useLocalStorage } from "@agir/lib/utils/hooks";

import Tooltip from "@agir/front/genericComponents/Tooltip";

import background from "./life-ring.svg";

const slideInTransition = {
  from: { opacity: 0, marginBottom: "-3rem" },
  enter: { opacity: 1, marginBottom: "0rem" },
  leave: { opacity: 0, marginBottom: "-3rem" },
};

const Button = styled.a`
  display: block;
  width: 100%;
  height: 100%;
  border-radius: 100%;
  background-color: transparent;
  background-image: url(${background});
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center center;
`;

const Wrapper = styled(animated.div)`
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  width: 4rem;
  height: 4rem;
  z-index: ${style.zindexFeedbackButton};

  @media (max-width: ${style.collapse}px) {
    width: 3rem;
    height: 3rem;
    bottom: 5rem;
  }
`;

export const FeedbackButton = (props) => {
  const { isActive, shouldPushTooltip, href } = props;
  const { isMobileApp } = useMobileApp();

  const [hasTooltip, setHasTooltip] = useState(false);

  const hideTooltip = useCallback(() => {
    setHasTooltip(false);
  }, []);

  const showTooltip = useCallback(() => {
    setHasTooltip(true);
  }, []);

  const pushTooltip = useCallback(() => {
    shouldPushTooltip && showTooltip();
  }, [shouldPushTooltip, showTooltip]);

  const wrapperTransition = useTransition(isActive, {
    ...slideInTransition,
    onRest: pushTooltip,
  });

  return wrapperTransition((style, item) =>
    item ? (
      <Wrapper style={{ ...(props.style || {}), ...style }}>
        <Tooltip
          position="top-left"
          shouldShow={hasTooltip}
          onClose={shouldPushTooltip ? hideTooltip : undefined}
        >
          <strong>Aidez-nous !</strong>
          {isMobileApp ? (
            <span>
              Donnez votre avis sur l'application Action Populaire&nbsp;→
            </span>
          ) : (
            <span>Donnez votre avis sur le site Action Populaire&nbsp;→</span>
          )}
        </Tooltip>
        <Button
          href={href}
          aria-label="Je donne mon avis"
          onMouseOver={shouldPushTooltip ? undefined : showTooltip}
          onMouseLeave={shouldPushTooltip ? undefined : hideTooltip}
        />
      </Wrapper>
    ) : null,
  );
};
FeedbackButton.propTypes = {
  isActive: PropTypes.bool,
  shouldPushTooltip: PropTypes.bool,
  href: PropTypes.string,
};
const ConnectedFeedbackButton = (props) => {
  const user = useSelector(getUser);
  const routes = useSelector(getRoutes);
  const [visitCount, setVisitCount] = useLocalStorage("AP_vcount", 0);

  const href = routes && routes.feedbackForm;

  const [shouldPushTooltip, setShouldPushTooltip] = useState(false);

  useEffectOnce(() => {
    const count = visitCount + 1;
    count % 20 === 3 && setShouldPushTooltip(true);
    setVisitCount(count);
  });

  return (
    <FeedbackButton
      {...props}
      href={href}
      shouldPushTooltip={shouldPushTooltip}
      isActive={!!user}
    />
  );
};
export default ConnectedFeedbackButton;
