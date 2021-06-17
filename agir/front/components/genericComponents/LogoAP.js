import PropTypes from "prop-types";
import styled from "styled-components";

import "@agir/front/genericComponents/_variables.scss";

import svgLogo from "@agir/front/genericComponents/logos/action-populaire.svg";
import svgLogoSmall from "@agir/front/genericComponents/logos/action-populaire_small.svg";

const LogoAP = styled.img.attrs(({ small }) => ({
  src: small ? svgLogoSmall : svgLogo,
  width: small ? "183" : "127",
  height: small ? "48" : "36",
}))`
  height: ${(props) => props.height || "auto"};
  width: ${(props) => props.width || "auto"};
`;

LogoAP.propTypes = {
  small: PropTypes.bool,
  width: PropTypes.string,
  height: PropTypes.string,
  alt: PropTypes.string,
};
LogoAP.defaultProps = {
  small: false,
  alt: "Action Populaire",
};

export default LogoAP;
