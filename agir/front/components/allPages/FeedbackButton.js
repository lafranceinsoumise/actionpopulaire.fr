import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import { useTransition, animated } from "react-spring";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getHasFeedbackButton,
  getUser,
  getRoutes,
} from "@agir/front/globalContext/reducers";

import Tooltip from "@agir/front/genericComponents/Tooltip";

import background from "./feedback-form-button.svg";

const slideInTransition = {
  from: { opacity: 0, marginBottom: "-3rem" },
  enter: { opacity: 1, marginBottom: "0" },
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
  bottom: 1rem;
  right: 1rem;
  width: 53px;
  height: 53px;
  z-index: ${style.zindexFeedbackButton};

  @media (max-width: ${style.collapse}px) {
    bottom: 75px;
  }
`;

export const FeedbackButton = (props) => {
  const { isActive, shouldPushTooltip, href } = props;
  const style = props.style || {};

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

  const wrapperTransition = useTransition(isActive, null, {
    ...slideInTransition,
    onRest: pushTooltip,
  });

  return wrapperTransition.map(({ item, key, props }) =>
    item ? (
      <Wrapper key={key} style={{ ...style, ...props }}>
        <Tooltip
          position="top-left"
          shouldShow={hasTooltip}
          onClose={shouldPushTooltip ? hideTooltip : undefined}
        >
          <strong>Aidez-nous !</strong>
          <span>Donnez votre avis sur le nouveau site →</span>
        </Tooltip>
        <Button
          href={href}
          aria-label="Je donne mon avis"
          onMouseOver={shouldPushTooltip ? undefined : showTooltip}
          onMouseLeave={shouldPushTooltip ? undefined : hideTooltip}
        />
      </Wrapper>
    ) : null
  );
};
FeedbackButton.propTypes = {
  isActive: PropTypes.bool,
  shouldPushTooltip: PropTypes.bool,
  href: PropTypes.string,
};
const ConnectedFeedbackButton = (props) => {
  const hasFeedbackButton = useSelector(getHasFeedbackButton);
  const user = useSelector(getUser);
  const routes = useSelector(getRoutes);

  const href = routes && routes.feedbackForm;

  const [isActive, setIsActive] = useState(false);
  const [shouldPushTooltip, setShouldPushTooltip] = useState(false);

  useEffect(() => {
    if (!window.localStorage) {
      return;
    }
    let visitCount = window.localStorage.getItem("AP_vcount");
    visitCount = !isNaN(parseInt(visitCount)) ? parseInt(visitCount) : 0;
    visitCount += 1;
    visitCount % 20 === 3 && setShouldPushTooltip(true);
    setIsActive(true);
    window.localStorage.setItem("AP_vcount", visitCount);
  }, []);

  return (
    <FeedbackButton
      {...props}
      href={href}
      // isActive={!!user && hasFeedbackButton && isActive}
      shouldPushTooltip={shouldPushTooltip}
      isActive
    />
  );
};
export default ConnectedFeedbackButton;
