import PropTypes from "prop-types";
import styled from "styled-components";

import "./_variables.scss";
import svgLogo from "./logos/action-populaire.svg";

const LogoAP = styled.img.attrs(() => ({ src: svgLogo }))`
  height: ${(props) => props.height || "auto"};
  width: ${(props) => props.width || "auto"};
`;
LogoAP.propTypes = {
  width: PropTypes.string,
  height: PropTypes.string,
  alt: PropTypes.string,
};

LogoAP.defaultProps = {
  alt: "Action Populaire",
};

export default LogoAP;
