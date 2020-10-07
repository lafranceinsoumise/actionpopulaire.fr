import React from "react";
import PropTypes from "prop-types";

import "./style.scss";
import svgLogo from "./logo.svg";

const LogoFI = ({ alt, height, width }) => {
  return <img src={svgLogo} alt={alt} style={{ height, width }} />;
};
LogoFI.propTypes = {
  width: PropTypes.number,
  height: PropTypes.number,
  alt: PropTypes.string,
};

LogoFI.defaultProps = {
  alt: "La France insoumise",
};

export default LogoFI;
