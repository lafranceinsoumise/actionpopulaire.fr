import { animated, useSpring } from "react-spring";
import PropTypes from "prop-types";
import React from "react";

export const PageFadeIn = ({ ready, wait, children }) => {
  const transition = useSpring({ opacity: 1, from: { opacity: 0 } });

  return ready ? (
    <animated.div style={transition}>{children}</animated.div>
  ) : (
    <>{wait}</>
  );
};

PageFadeIn.propTypes = {
  ready: PropTypes.any,
  wait: PropTypes.node,
  children: PropTypes.node,
};

export default PageFadeIn;
