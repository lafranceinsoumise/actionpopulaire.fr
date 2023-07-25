import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

const Counter = ({ value, ...rest }) =>
  !!value ? (
    <svg
      {...rest}
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="8" cy="8" r="8" fill="inherit" stroke="none" />
      <text
        x="8"
        y="8"
        dominantBaseline="central"
        textAnchor="middle"
        fontSize={String(value).length > 1 ? "8px" : "10px"}
        fontWeight="700"
        fill="#FFFFFF"
      >
        {!isNaN(value) && parseInt(value) > 20 ? "+20" : value}
      </text>
    </svg>
  ) : null;

Counter.propTypes = {
  value: PropTypes.number,
};

const CounterBadge = styled(Counter)`
  fill: ${(props) => props.$background || props.theme.redNSP};
  z-index: ${(props) => props.theme.zindexNavigationCounter};

  circle {
    stroke: ${(props) => props.$border || "none"};
  }

  text {
    fill: ${(props) => props.$color || props.theme.white};
  }
`;

export default CounterBadge;
