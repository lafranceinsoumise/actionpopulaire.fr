import PropTypes from "prop-types";
import React, { forwardRef } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { ICONS, getIconDataUrl } from "./utils";

import BaseButton from "./BaseButton";

const DefaultButton = styled(BaseButton)`
  color: ${style.black1000};
  background-color: ${style.black50};
  border-color: ${style.black50};

  &:hover,
  &:focus,
  &:active {
    color: ${style.black1000};
    background-color: ${style.black100};
    border-color: ${style.black100};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${style.black1000 + "4D"};
    background-color: ${style.black50 + "B7"};
    border-color: ${style.black50 + "B7"};

    &:before {
      background-image: ${getIconDataUrl({
        color: style.black1000 + "4D",
      })};
    }
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.black1000 })};
  }
`;

const WhiteButton = styled(BaseButton)`
  &,
  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${style.primary500};
    background-color: ${style.white};
    border-color: ${style.white};
  }

  &[disabled] {
    opacity: 0.75;
  }

  &:hover,
  &:focus,
  &:active {
    color: ${style.primary500};
    background-color: ${style.black50};
    border-color: ${style.black50};
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.primary500 })};
  }
`;

const WhiteRedButton = styled(BaseButton)`
  &,
  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${style.redNSP};
    background-color: ${style.white};
    border-color: ${style.white};
  }

  &[disabled] {
    opacity: 0.75;
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.redNSP })};
  }

  &:hover,
  &:focus,
  &:active {
    color: #d81836;

    &:before {
      background-image: ${getIconDataUrl({
        color: "#d81836",
        fill: true,
      })};
    }
  }
`;

const PrimaryButton = styled(BaseButton)`
  background-color: ${style.primary500};
  border-color: ${style.primary500};
  color: ${style.white};

  &:hover,
  &:focus,
  &:active {
    color: ${style.white};
    background-color: ${style.primary600};
    border-color: ${style.primary600};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${style.white + "B7"};
    background-color: ${style.primary500 + "B7"};
    border-color: ${style.primary500 + "B7"};
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.white })};
  }
`;

const SecondaryButton = styled(BaseButton)`
  color: ${style.black1000};
  background-color: ${style.secondary500};
  border-color: ${style.secondary500};

  &:hover,
  &:focus,
  &:active {
    color: ${style.black1000};
    background-color: ${style.secondary600};
    border-color: ${style.secondary600};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    background-color: ${style.secondary500 + "B7"};
    border-color: ${style.secondary500 + "B7"};
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.black1000 })};
  }
`;

const TertiaryButton = styled(BaseButton)`
  &,
  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    background-color: ${style.white};
    border-color: ${style.primary500};
    color: ${style.primary500};
  }

  &[disabled] {
    opacity: 0.75;
  }

  &:hover,
  &:focus,
  &:active {
    background-color: ${style.black50};
    border-color: ${style.primary600};
    color: ${style.primary600};
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.primary500 })};
  }
`;

const ConfirmedButton = styled(BaseButton)`
  color: ${style.primary500};
  background-color: ${style.primary100};
  border-color: ${style.primary100};

  &:hover,
  &:focus,
  &:active {
    color: ${style.primary500};
    background-color: ${style.primary150};
    border-color: ${style.primary150};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${style.primary500 + "4D"};
    background-color: ${style.primary100 + "B7"};
    border-color: ${style.primary100 + "B7"};

    &:before {
      background-image: ${getIconDataUrl({ color: style.primary500 + "4D" })};
    }
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.primary500 })};
  }
`;

const UnavailableButton = styled(BaseButton)`
  color: ${style.black500};
  background-color: ${style.white};
  border-color: ${style.black100};

  &:hover,
  &:focus,
  &:active {
    color: ${style.black500};
  }

  &[disabled] {
    color: ${style.black500 + "4D"};
    border-color: ${style.black100 + "B7"};

    &:before {
      background-image: ${getIconDataUrl({ color: style.black500 + "4D" })};
    }
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.black500 })};
  }
`;
const DismissButton = styled(BaseButton)`
  color: ${style.black1000};
  background-color: transparent;
  border-color: ${style.black1000};

  &:hover,
  &:focus,
  &:active {
    color: ${style.black1000};
  }

  &[disabled] {
    color: ${style.black1000 + "4D"};
    border-color: ${style.black1000 + "4D"};

    &:before {
      background-image: ${getIconDataUrl({ color: style.black1000 + "4D" })};
    }
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.black1000 })};
  }
`;
const ChooseButton = styled(BaseButton)`
  color: ${style.black1000};
  background-color: transparent;
  border-color: ${style.black200};

  &:hover,
  &:focus,
  &:active {
    color: ${style.black1000};
    background-color: ${style.black50};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${style.black1000 + "4D"};
    background-color: ${style.black50 + "B7"};
    border-color: ${style.black50 + "B7"};

    &:before {
      background-image: ${getIconDataUrl({ color: style.black1000 + "4D" })};
    }
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.black1000 })};
  }
`;
const SuccessButton = styled(BaseButton)`
  color: ${style.white};
  background-color: ${style.green500};
  border-color: ${style.green500};

  &:hover,
  &:focus,
  &:active {
    color: ${style.white};
  }

  &[disabled] {
    background-color: ${style.green500 + "4D"};
    border-color: ${style.green500 + "4D"};
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.white })};
  }
`;
const DangerButton = styled(BaseButton)`
  color: ${style.white};
  background-color: ${style.redNSP};
  border-color: ${style.redNSP};

  &:hover,
  &:focus,
  &:active {
    color: ${style.white};
    background-color: #d81836;
    border-color: #d81836;
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    background-color: ${style.redNSP + "B7"};
    border-color: ${style.redNSP + "B7"};
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.white })};
  }
`;
const FacebookButton = styled(BaseButton)`
  color: ${style.white};
  background-color: ${style.facebook};
  border-color: ${style.facebook};

  &:hover,
  &:focus,
  &:active {
    color: ${style.white};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    background-color: #1778f2b7;
    border-color: #1778f2b7;
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.white })};
  }
`;
const LinkButton = styled(BaseButton)`
  font-size: inherit;
  font-weight: inherit;
  padding-left: 0;
  padding-right: 0;
  color: ${style.primary500};
  background-color: transparent;
  border-color: transparent;

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    opacity: 0.75;
    text-decoration: none;
  }

  &:hover,
  &:focus,
  &:active {
    color: ${style.primary500};
    text-decoration: underline;
  }

  &:before {
    background-image: ${getIconDataUrl({ color: style.primary500 })};
  }
`;

const variants = {
  default: DefaultButton,
  white: WhiteButton,
  whiteRed: WhiteRedButton,
  primary: PrimaryButton,
  secondary: SecondaryButton,
  tertiary: TertiaryButton,
  confirmed: ConfirmedButton,
  unavailable: UnavailableButton,
  dismiss: DismissButton,
  choose: ChooseButton,
  success: SuccessButton,
  danger: DangerButton,
  facebook: FacebookButton,
  link: LinkButton,
};

const Button = styled(
  // eslint-disable-next-line react/display-name
  forwardRef((props, ref) => {
    // eslint-disable-next-line react/prop-types
    const { color } = props;
    const B = color && variants[color] ? variants[color] : variants.default;
    return <B ref={ref} {...props} />;
  }),
)``;

Button.icons = Object.keys(ICONS);
Button.colors = Object.keys(variants);
Button.propTypes = {
  ...BaseButton.propTypes,
  color: PropTypes.string,
};
export default Button;
