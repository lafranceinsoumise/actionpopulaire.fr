import { icons } from "feather-icons";
import PropTypes from "prop-types";
import styled from "styled-components";

import Link from "@agir/front/app/Link";

export const buttonColors = (theme) => ({
  default: {
    $background: theme.text50,
    $hoverBackground: theme.text100,
    $labelColor: theme.text1000,
  },
  white: {
    $background: theme.background0,
    $hoverBackground: theme.text50,
    $labelColor: theme.primary500,
  },
  primary: {
    $background: theme.primary500,
    $labelColor: theme.background0,
    $hoverBackground: theme.primary600,
  },
  secondary: {
    $background: theme.secondary500,
    $labelColor: theme.text1000,
    $hoverBackground: theme.secondary600,
  },
  tertiary: {
    $background: theme.background0,
    $labelColor: theme.primary500,
    $hoverLabelColor: theme.primary600,
    $borderColor: theme.primary500,
    $hoverBorderColor: theme.primary600,
  },
  confirmed: {
    $background: theme.primary100,
    $hoverBackground: theme.primary150,
    $labelColor: theme.primary500,
  },
  unavailable: {
    $background: theme.background0,
    $hoverBackground: theme.background0,
    $labelColor: theme.text500,
    $borderColor: theme.text100,
  },
  dismiss: {
    $background: "transparent",
    $labelColor: theme.text1000,
    $hoverBackground: "transparent",
    $borderColor: theme.text1000,
  },
  choose: {
    $background: "transparent",
    $labelColor: theme.text1000,
    $hoverBackground: theme.text50,
    $borderColor: theme.text200,
  },
  success: {
    $background: theme.success500,
    $labelColor: theme.background0,
    $hoverBackground: theme.success500,
  },
  danger: {
    $background: theme.error500,
    $labelColor: theme.background0,
    $hoverBackground: "#d81836",
  },
  link: {
    $background: theme.background0,
    $hoverBackground: theme.background0,
    $labelColor: theme.primary500,
    style: {
      textDecoration: "underline",
      fontSize: "inherit",
      fontWeight: "inherit",
      paddingLeft: 0,
      paddingRight: 0,
    },
  },
});

/**
 * Pour une raison obscure, lorsque la taille dédiée au contenu (telle que déterminée par min-height)
 */
export const Button = styled.button.attrs(
  ({ color, small, block, $wrap, icon, as, $hasTransition, theme }) => ({
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
    ...buttonColors(theme)[color],
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
  border-radius: ${(props) => props.theme.borderRadius};

  text-align: center;
  font-weight: 500;
  font-size: ${({ $small }) => ($small ? "0.875rem" : "1rem")};

  color: ${({ $labelColor, disabled, theme }) =>
    disabled && $labelColor !== theme.background0
      ? $labelColor + "4D"
      : $labelColor};
  background-color: ${({ $background, disabled, theme }) =>
    disabled && $background !== theme.background0
      ? $background + "B7"
      : $background};
  border: 1px solid transparent;
  border-color: ${({ $borderColor, $background, disabled, theme }) => {
    if (!$borderColor || !$background) return "transparent";
    if ($borderColor) return $borderColor;
    if (disabled && $background !== theme.background0)
      return $background + "B3";
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
    color: ${({ $hoverLabelColor, $labelColor, disabled, theme }) =>
      disabled && $labelColor !== theme.background0
        ? $labelColor + "4D"
        : $hoverLabelColor || $labelColor};
    border-color: ${({
      $hoverBorderColor,
      $borderColor,
      $background,
      disabled,
      theme,
    }) => {
      if (!$borderColor || !$background) return "transparent";
      if ($hoverBorderColor) return $hoverBorderColor;
      if ($borderColor) return $borderColor;
      if (disabled && $background !== theme.background0)
        return $background + "B7";
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
  small: false,
  block: false,
};

export default Button;
