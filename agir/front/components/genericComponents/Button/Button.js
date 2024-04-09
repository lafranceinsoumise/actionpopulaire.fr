import PropTypes from "prop-types";
import React, { forwardRef } from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { ICONS, getIconDataUrl } from "./utils";

import BaseButton from "./BaseButton";

const DefaultButton = styled(BaseButton)`
  color: ${(props) => props.theme.black1000};
  background-color: ${(props) => props.theme.black50};
  border-color: ${(props) => props.theme.black50};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.black1000};
    background-color: ${(props) => props.theme.black100};
    border-color: ${(props) => props.theme.black100};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${(props) => props.theme.black1000 + "4D"};
    background-color: ${(props) => props.theme.black50 + "B7"};
    border-color: ${(props) => props.theme.black50 + "B7"};

    &:before {
      background-image: ${(props) =>
        getIconDataUrl({
          color: props.theme.black1000 + "4D",
        })};
    }
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.black1000 })};
  }
`;

const WhiteButton = styled(BaseButton)`
  &,
  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${(props) => props.theme.primary500};
    background-color: ${(props) => props.theme.white};
    border-color: ${(props) => props.theme.white};
  }

  &[disabled] {
    opacity: 0.75;
  }

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.primary500};
    background-color: ${(props) => props.theme.black50};
    border-color: ${(props) => props.theme.black50};
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.primary500 })};
  }
`;

const WhiteRedButton = styled(BaseButton)`
  &,
  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${(props) => props.theme.redNSP};
    background-color: ${(props) => props.theme.white};
    border-color: ${(props) => props.theme.white};
  }

  &[disabled] {
    opacity: 0.75;
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.redNSP })};
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

const TransparentButton = styled(BaseButton)`
  &,
  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${(props) => props.theme.primary500};
    background-color: transparent;
    border-color: transparent;
  }

  &[disabled] {
    opacity: 0.75;
  }

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.primary600};
    background-color: ${(props) => props.theme.black50};
    border-color: ${(props) => props.theme.black50};
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.primary500 })};
  }
`;

const PrimaryButton = styled(BaseButton)`
  background-color: ${(props) => props.theme.primary500};
  border-color: ${(props) => props.theme.primary500};
  color: ${(props) => props.theme.white};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.white};
    background-color: ${(props) => props.theme.primary600};
    border-color: ${(props) => props.theme.primary600};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${(props) => props.theme.white + "B7"};
    background-color: ${(props) => props.theme.primary500 + "B7"};
    border-color: ${(props) => props.theme.primary500 + "B7"};
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.white })};
  }
`;

const SecondaryButton = styled(BaseButton)`
  color: ${(props) => props.theme.black1000};
  background-color: ${(props) => props.theme.secondary500};
  border-color: ${(props) => props.theme.secondary500};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.black1000};
    background-color: ${(props) => props.theme.secondary600};
    border-color: ${(props) => props.theme.secondary600};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    background-color: ${(props) => props.theme.secondary500 + "B7"};
    border-color: ${(props) => props.theme.secondary500 + "B7"};
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.black1000 })};
  }
`;

const TertiaryButton = styled(BaseButton)`
  &,
  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    background-color: ${(props) => props.theme.white};
    border-color: ${(props) => props.theme.primary500};
    color: ${(props) => props.theme.primary500};
  }

  &[disabled] {
    opacity: 0.75;
  }

  &:hover,
  &:focus,
  &:active {
    background-color: ${(props) => props.theme.black50};
    border-color: ${(props) => props.theme.primary600};
    color: ${(props) => props.theme.primary600};
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.primary500 })};
  }
`;

const ConfirmedButton = styled(BaseButton)`
  color: ${(props) => props.theme.primary500};
  background-color: ${(props) => props.theme.primary100};
  border-color: ${(props) => props.theme.primary100};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.primary500};
    background-color: ${(props) => props.theme.primary150};
    border-color: ${(props) => props.theme.primary150};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${(props) => props.theme.primary500 + "4D"};
    background-color: ${(props) => props.theme.primary100 + "B7"};
    border-color: ${(props) => props.theme.primary100 + "B7"};

    &:before {
      background-image: ${(props) =>
        getIconDataUrl({ color: props.theme.primary500 + "4D" })};
    }
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.primary500 })};
  }
`;

const UnavailableButton = styled(BaseButton)`
  color: ${(props) => props.theme.black500};
  background-color: ${(props) => props.theme.white};
  border-color: ${(props) => props.theme.black100};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.black500};
  }

  &[disabled] {
    color: ${(props) => props.theme.black500 + "4D"};
    border-color: ${(props) => props.theme.black100 + "B7"};

    &:before {
      background-image: ${(props) =>
        getIconDataUrl({ color: props.theme.black500 + "4D" })};
    }
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.black500 })};
  }
`;
const DismissButton = styled(BaseButton)`
  color: ${(props) => props.theme.black1000};
  background-color: transparent;
  border-color: ${(props) => props.theme.black1000};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.black1000};
  }

  &[disabled] {
    color: ${(props) => props.theme.black1000 + "4D"};
    border-color: ${(props) => props.theme.black1000 + "4D"};

    &:before {
      background-image: ${(props) =>
        getIconDataUrl({ color: props.theme.black1000 + "4D" })};
    }
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.black1000 })};
  }
`;
const ChooseButton = styled(BaseButton)`
  color: ${(props) => props.theme.black1000};
  background-color: transparent;
  border-color: ${(props) => props.theme.black200};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.black1000};
    background-color: ${(props) => props.theme.black50};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${(props) => props.theme.black1000 + "4D"};
    background-color: ${(props) => props.theme.black50 + "B7"};
    border-color: ${(props) => props.theme.black50 + "B7"};

    &:before {
      background-image: ${(props) =>
        getIconDataUrl({ color: props.theme.black1000 + "4D" })};
    }
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.black1000 })};
  }
`;
const SuccessButton = styled(BaseButton)`
  color: ${(props) => props.theme.white};
  background-color: ${(props) => props.theme.green500};
  border-color: ${(props) => props.theme.green500};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.white};
  }

  &[disabled] {
    background-color: ${(props) => props.theme.green500 + "4D"};
    border-color: ${(props) => props.theme.green500 + "4D"};
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.white })};
  }
`;
const DangerButton = styled(BaseButton)`
  color: ${(props) => props.theme.white};
  background-color: ${(props) => props.theme.redNSP};
  border-color: ${(props) => props.theme.redNSP};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.white};
    background-color: #d81836;
    border-color: #d81836;
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    background-color: ${(props) => props.theme.redNSP + "B7"};
    border-color: ${(props) => props.theme.redNSP + "B7"};
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.white })};
  }
`;
const FacebookButton = styled(BaseButton)`
  color: ${(props) => props.theme.white};
  background-color: ${(props) => props.theme.facebook};
  border-color: ${(props) => props.theme.facebook};

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.white};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    background-color: #1778f2b7;
    border-color: #1778f2b7;
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.white })};
  }
`;
const LinkButton = styled(BaseButton)`
  font-size: inherit;
  font-weight: inherit;
  padding-left: 0;
  padding-right: 0;
  color: ${(props) => props.theme.primary500};
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
    color: ${(props) => props.theme.primary500};
    text-decoration: underline;
  }

  &:before {
    background-image: ${(props) =>
      getIconDataUrl({ color: props.theme.primary500 })};
  }
`;

const variants = {
  default: DefaultButton,
  white: WhiteButton,
  whiteRed: WhiteRedButton,
  transparent: TransparentButton,
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
