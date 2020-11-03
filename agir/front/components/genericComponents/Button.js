import style from "./_variables.scss";
import styled from "styled-components";
import PropTypes from "prop-types";
import { transparentize } from "polished";
import { icons } from "feather-icons";

const buttonColors = {
  default: {
    background: style.black50,
    hoverBackground: style.black100,
    labelColor: style.black1000,
  },
  primary: {
    background: style.primary500,
    labelColor: style.white,
    hoverBackground: style.primary600,
  },
  secondary: {
    background: style.secondary500,
    labelColor: style.white,
    hoverBackground: style.secondary600,
  },
  confirmed: {
    background: style.primary100,
    hoverBackground: style.primary150,
    labelColor: style.primary500,
  },
  unavailable: {
    background: style.white,
    hoverBackground: style.white,
    labelColor: style.black500,
    borderColor: style.black100,
  },
  dismiss: {
    background: "transparent",
    labelColor: style.primary600,
    hoverBackground: "transparent",
    borderColor: style.primary600,
  },
};

const Button = styled.button.attrs(({ color }) => buttonColors[color])`
  display: inline-block;
  padding: ${({ small }) => (small ? "0.5rem 0.75rem" : "0.75rem 1.5rem")};
  line-height: ${({ small }) =>
    small
      ? "95%"
      : "1.5rem"}; /* pour s'assurer que les liens sont correctement centrés */
  margin: 0;
  border-radius: 0.5rem;
  min-height: ${({ small }) => (small ? "2rem" : "3rem")};
  text-align: center;
  font-weight: 700;
  font-size: ${({ small }) => (small ? "0.6875rem" : "0.875rem")};

  color: ${({ labelColor, disabled }) =>
    disabled ? transparentize(0.3, labelColor) : labelColor};
  background-color: ${({ background, disabled }) =>
    disabled ? transparentize(0.7, background) : background};
  border: ${({ borderColor, background, disabled }) => {
    if (!borderColor || !background) return "0";
    if (borderColor) return `1px solid ${borderColor}`;
    return disabled ? transparentize(0.7, background) : background;
  }}}

  &:hover {
    ${({ disabled, hoverBackground }) =>
      disabled
        ? ""
        : `background-color: ${hoverBackground};`} // disabled buttons must not change color on hover
    text-decoration: none;
    color: ${({ labelColor }) =>
      labelColor}; // we need to overwrite link hover colors
  }

  ${({ disabled }) => disabled && "cursor: not-allowed;"}

  ${({ icon, labelColor, small }) =>
    icon
      ? `
    &:before {
      content: url('data:image/svg+xml;utf8,${
        icons[icon]
          .toSvg({
            color: encodeURI(labelColor),
            height: small ? 11 : 16,
            width: small ? 11 : 16,
          })
          .replace("#", "%23")
        /*
         * problème bizarre, quand le SVG est utilisé dans un URL data:
         * Il faut remplacer les # des couleurs par l'équivalent url-encoded, mais
         * appliquer la même procédure aux autres substitutions (avec encodeURI par
         * exemple) ne fonctionne pas.
         *  */
      }');
      position: relative;
      top: 0.15rem;
      margin-right: ${small ? "0.25rem" : "0.5rem"};
    }
  `
      : ""}
}}
`;

Button.colors = Object.keys(buttonColors);

Button.propTypes = {
  onClick: PropTypes.func,
  color: PropTypes.oneOf(Button.colors),
  small: PropTypes.bool,
  disabled: PropTypes.bool,
  href: PropTypes.string,
  block: PropTypes.bool,
};

Button.defaultProps = {
  color: "default",
  small: false,
  block: false,
};

export default Button;
