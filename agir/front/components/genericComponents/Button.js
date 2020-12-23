import PropTypes from "prop-types";
import React from "react";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

import { transparentize } from "polished";
import { icons } from "feather-icons";
import Link from "@agir/front/app/Link";

const buttonColors = {
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
};

/**
 * Pour une raison obscure, lorsque la taille dédiée au contenu (telle que déterminée par min-height)
 */
export const Button = styled.button.attrs(({ $color }) => buttonColors[$color])`
  display: ${({ $block }) => ($block ? "flex" : "inline-flex")};;
  align-items: center;
  white-space: nowrap;
  padding: ${({ $small }) => ($small ? "0.5rem 0.75rem" : "0.75rem 1.5rem")};
  line-height: ${({ $small }) =>
    $small
      ? "1rem"
      : "1.5rem"}; /* pour s'assurer que les liens sont correctement centrés */
  margin: 0;
  border-radius: ${style.defaultBorderRadius};

  text-align: center;
  font-weight: 700;
  font-size: ${({ $small }) => ($small ? "0.875rem" : "1rem")};

  color: ${({ $labelColor, disabled }) =>
    disabled ? transparentize(0.3, $labelColor) : $labelColor};
  background-color: ${({ $background, disabled }) =>
    disabled ? transparentize(0.7, $background) : $background};
  border: 1px solid transparent;
  border-color: ${({ $borderColor, $background, disabled }) => {
    if (!$borderColor || !$background) return "transparent";
    if ($borderColor) return $borderColor;
    if (disabled) return transparentize(0.7, $background);
    return $background;
  }}}
  cursor: pointer;

  & + & {
    margin-left: ${({ $block }) => ($block ? "0" : "0.5rem")};
  }

  &:hover,
  &:focus,
  &:active {
    ${({ disabled, $hoverBackground }) =>
      disabled
        ? ""
        : `background-color: ${$hoverBackground};`} // disabled buttons must not change color on hover
    text-decoration: none;
    color: ${({ $hoverLabelColor, $labelColor, disabled }) =>
      disabled
        ? transparentize(0.3, $labelColor)
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
      if (disabled) return transparentize(0.7, $background);
      return $background;
    }}}
  }

  ${({ disabled }) => disabled && "cursor: not-allowed;"}

  ${({ $icon, $labelColor, $small }) =>
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
          })
          .replace("#", "%23")
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
  $color: PropTypes.oneOf(Button.colors),
  $small: PropTypes.bool,
  $block: PropTypes.bool,
  $icon: PropTypes.string,
};

Button.defaultProps = {
  $color: "default",
  $small: false,
  $block: false,
};

export const ButtonElement = React.forwardRef((props, ref) => {
  const {
    as,
    onClick,
    color,
    small,
    disabled,
    href,
    block,
    icon,
    ...rest
  } = props;
  const Btn = (
    <Button
      ref={ref}
      onClick={onClick}
      href={href}
      disabled={disabled}
      as={as}
      $color={color}
      $small={small}
      $block={block}
      $icon={icon}
      {...rest}
    />
  );

  return Btn;
});

ButtonElement.propTypes = {
  as: PropTypes.elementType,
  onClick: PropTypes.func,
  href: PropTypes.string,
  disabled: PropTypes.bool,
  color: PropTypes.oneOf(Button.colors),
  small: PropTypes.bool,
  block: PropTypes.bool,
  icon: PropTypes.string,
};
ButtonElement.displayName = "ButtonElement";

const RouterButton = ({ as, ...props }) =>
  as === "Link" ? (
    <ButtonElement as={Link} {...props} />
  ) : (
    <ButtonElement as={as} {...props} />
  );

RouterButton.propTypes = {
  as: PropTypes.elementType,
};

export default RouterButton;
