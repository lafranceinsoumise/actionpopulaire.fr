import PropTypes from "prop-types";
import styled from "styled-components";

import "./_variables.scss";
import svgLogo from "./logos/LFI-NUPES-Violet-H.webp";

const LogoFI = styled.img.attrs(() => ({ src: svgLogo }))`
  height: ${(props) => props.height || "auto"};
  width: ${(props) => props.width || "auto"};
`;
LogoFI.propTypes = {
  width: PropTypes.string,
  height: PropTypes.string,
  alt: PropTypes.string,
};

LogoFI.defaultProps = {
  alt: "La France insoumise",
};

export default LogoFI;
