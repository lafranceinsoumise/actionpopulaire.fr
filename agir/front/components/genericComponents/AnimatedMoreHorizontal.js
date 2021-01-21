import PropTypes from "prop-types";
import React, { useState } from "react";
import { useTrail, animated } from "react-spring";

const MoreHorizontal = (props) => {
  const { color, size, ...otherProps } = props;
  const [reset, setReset] = useState(false);

  const trail = useTrail(3, {
    config: { mass: 1, tension: 200, friction: 60 },
    opacity: reset ? 0 : 1,
    from: { opacity: reset ? 1 : 0 },
    onRest: () => setReset((reset) => !reset),
  });

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...otherProps}
    >
      {trail.map((style, index) => (
        <animated.circle
          key={index}
          style={style}
          cx={index * 7 + 5}
          cy="12"
          r="1"
        />
      ))}
    </svg>
  );
};

MoreHorizontal.propTypes = {
  color: PropTypes.string,
  size: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

MoreHorizontal.defaultProps = {
  color: "currentColor",
  size: "24",
};

export default MoreHorizontal;
