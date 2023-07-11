import isPropValid from "@emotion/is-prop-valid";
import PropTypes from "prop-types";
import styled from "styled-components";

import "@agir/front/genericComponents/_variables.scss";

import svgLogo from "@agir/front/genericComponents/logos/action-populaire.svg";
import svgLogoSmall from "@agir/front/genericComponents/logos/action-populaire_small.svg";

const LogoAP = styled.img
  .withConfig({
    shouldForwardProp: isPropValid,
  })
  .attrs(({ small }) => ({
    src: small ? svgLogoSmall : svgLogo,
    width: small ? "182" : "149",
    height: small ? "35" : "56",
  }))`
  font-size: 0;
  color: transparent;
  height: ${(props) => props.height + "px" || "auto"};
  width: ${(props) => props.width + "px" || "auto"};
  vertical-align: unset;
`;

LogoAP.propTypes = {
  small: PropTypes.bool,
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  alt: PropTypes.string,
};
LogoAP.defaultProps = {
  small: false,
  alt: "Action Populaire",
};

export default LogoAP;
