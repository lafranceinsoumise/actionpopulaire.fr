import { animated, useSpring } from "@react-spring/web";
import PropTypes from "prop-types";
import React from "react";

export const PageFadeIn = ({ ready, wait, children, className }) => {
  const transition = useSpring({ opacity: 1, from: { opacity: 0 } });

  return ready ? (
    <animated.div className={className} style={transition}>
      {children}
    </animated.div>
  ) : (
    <>{wait}</>
  );
};

PageFadeIn.propTypes = {
  ready: PropTypes.any,
  wait: PropTypes.node,
  children: PropTypes.node,
  className: PropTypes.string,
};

export default PageFadeIn;
