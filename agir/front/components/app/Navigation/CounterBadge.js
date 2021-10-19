import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

const Counter = ({ value, ...rest }) =>
  !isNaN(parseInt(value)) && value > 0 ? (
    <svg
      {...rest}
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="8" cy="8" r="8" fill="inherit" />
      <text
        x="8"
        y="8"
        dominantBaseline="central"
        textAnchor="middle"
        fontSize={String(value).length > 1 ? "8px" : "10px"}
        fontWeight="700"
        fill="#FFFFFF"
      >
        {String(value).length > 2 ? "+99" : value}
      </text>
    </svg>
  ) : null;

Counter.propTypes = {
  value: PropTypes.number,
};

const CounterBadge = styled(Counter)`
  fill: ${(props) => props.theme.redNSP};
  z-index: ${(props) => props.theme.zindexNavigationCounter};

  text {
    fill: ${(props) => props.theme.white};
  }
`;
export default CounterBadge;
