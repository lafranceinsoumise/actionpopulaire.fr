import PropTypes from "prop-types";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

import { icons } from "feather-icons";
import Link from "@agir/front/app/Link";

export const buttonColors = {
  default: {
    $background: style.black50,
    $hoverBackground: style.black100,
    $labelColor: style.black1000,
  },
  white: {
    $background: style.white,
    $hoverBackground: style.black50,
    $labelColor: style.primary500,
  },
  primary: {
    $background: style.primary500,
    $labelColor: style.white,
    $hoverBackground: style.primary600,
  },
  secondary: {
    $background: style.secondary500,
    $labelColor: style.black1000,
    $hoverBackground: style.secondary600,
  },
  tertiary: {
    $background: style.white,
    $labelColor: style.primary500,
    $hoverLabelColor: style.primary600,
    $borderColor: style.primary500,
    $hoverBorderColor: style.primary600,
  },
  confirmed: {
    $background: style.primary100,
    $hoverBackground: style.primary150,
    $labelColor: style.primary500,
  },
  unavailable: {
    $background: style.white,
    $hoverBackground: style.white,
    $labelColor: style.black500,
    $borderColor: style.black100,
  },
  dismiss: {
    $background: "transparent",
    $labelColor: style.black1000,
    $hoverBackground: "transparent",
    $borderColor: style.black1000,
  },
  choose: {
    $background: "transparent",
    $labelColor: style.black1000,
    $hoverBackground: style.black50,
    $borderColor: style.black200,
  },
  success: {
    $background: style.green500,
    $labelColor: style.white,
    $hoverBackground: style.green500,
  },
  danger: {
    $background: style.redNSP,
    $labelColor: style.white,
    $hoverBackground: "#d81836",
  },
  link: {
    $background: style.white,
    $hoverBackground: style.white,
    $labelColor: style.primary500,
    style: {
      textDecoration: "underline",
      fontSize: "inherit",
      fontWeight: "inherit",
      paddingLeft: 0,
      paddingRight: 0,
    },
  },
};

/**
 * Pour une raison obscure, lorsque la taille dédiée au contenu (telle que déterminée par min-height)
 */
export const Button = styled.button.attrs(
  ({ color, small, block, $wrap, icon, as, $hasTransition }) => ({
    $hasTransition,
    $wrap,
    $color: color,
    $small: small,
    $block: block,
    $icon: icon,
    color: null,
    small: null,
    block: null,
    icon: null,
    ...buttonColors[color],
    as: as === "Link" ? Link : as,
  }),
)`
  display: ${({ $block }) => ($block ? "flex" : "inline-flex")};
  width: ${({ $block }) => ($block ? "100%" : "auto")};
  align-items: center;
  justify-content: center;
  white-space: ${({ $wrap }) => ($wrap ? "normal" : "nowrap")};
  padding: ${({ $small }) => ($small ? "0.5rem 0.75rem" : "0.75rem 1.5rem")};
  line-height: ${({ $small }) =>
    $small
      ? "1rem"
      : "1.5rem"}; /* pour s'assurer que les liens sont correctement centrés */
  margin: 0;
  border-radius: ${style.borderRadius};

  text-align: center;
  font-weight: 500;
  font-size: ${({ $small }) => ($small ? "0.875rem" : "1rem")};

  color: ${({ $labelColor, disabled }) =>
    disabled && $labelColor !== style.white ? $labelColor + "4D" : $labelColor};
  background-color: ${({ $background, disabled }) =>
    disabled && $background !== style.white ? $background + "B7" : $background};
  border: 1px solid transparent;
  border-color: ${({ $borderColor, $background, disabled }) => {
    if (!$borderColor || !$background) return "transparent";
    if ($borderColor) return $borderColor;
    if (disabled && $background !== style.white) return $background + "B3";
    return $background;
  }}}
  cursor: pointer;
  ${({ $hasTransition }) =>
    $hasTransition ? "transition: all 250ms ease-in;" : ""}

  &:hover,
  &:focus,
  &:active {
    ${({ disabled, $hoverBackground }) =>
      disabled
        ? ""
        : `background-color: ${$hoverBackground};`} // disabled buttons must not change color on hover
    text-decoration: none;
    color: ${({ $hoverLabelColor, $labelColor, disabled }) =>
      disabled && $labelColor !== style.white
        ? $labelColor + "4D"
        : $hoverLabelColor || $labelColor};
    border-color: ${({
      $hoverBorderColor,
      $borderColor,
      $background,
      disabled,
    }) => {
      if (!$borderColor || !$background) return "transparent";
      if ($hoverBorderColor) return $hoverBorderColor;
      if ($borderColor) return $borderColor;
      if (disabled && $background !== style.white) return $background + "B7";
      return $background;
    }}}
  }

  ${({ disabled }) => disabled && "cursor: not-allowed;"}

  ${({ $icon, $iconFill, $labelColor, $small }) =>
    $icon
      ? `
    &:before {
      content: "";
      display: inline-block;
      height: ${$small ? "16px" : "16px"};
      width: ${$small ? "16px" : "16px"};
      background-size: contain;
      background-repeat: no-repeat;
      background-position: center center;
      background-image: url('data:image/svg+xml;utf8,${
        icons[$icon]
          .toSvg({
            color: encodeURI($labelColor),
            fill: $iconFill ? "currentColor" : "none",
          })
          .replace(/#/g, "%23")
        /*
         * problème bizarre, quand le SVG est utilisé dans un URL data:
         * Il faut remplacer les # des couleurs par l'équivalent url-encoded, mais
         * appliquer la même procédure aux autres substitutions (avec encodeURI par
         * exemple) ne fonctionne pas.
         *  */
      }');
      margin-right: ${$small ? "0.375rem" : "0.5rem"};
    }
  `
      : ""}
}}
`;

Button.colors = Object.keys(buttonColors);

Button.propTypes = {
  onClick: PropTypes.func,
  href: PropTypes.string,
  disabled: PropTypes.bool,
  color: PropTypes.oneOf(Button.colors),
  small: PropTypes.bool,
  block: PropTypes.bool,
  $wrap: PropTypes.bool,
  icon: PropTypes.string,
  $hasTransition: PropTypes.bool,
};

Button.defaultProps = {
  $background: style.black50,
  $hoverBackground: style.black100,
  $labelColor: style.black1000,
  small: false,
  block: false,
};

export default Button;
