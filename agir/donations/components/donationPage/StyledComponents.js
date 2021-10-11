import PropTypes from "prop-types";
import React from "react";
import styled, { ThemeProvider } from "styled-components";

import BaseButton from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import AppLink from "@agir/front/app/Link";

import CONFIG from "./config";

export const Link = styled(AppLink)`
  color: ${(props) => props.theme.primary500};
  text-decoration: underline;

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.primary600};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    color: ${(props) => props.theme.primary500};
  }
`;

export const Button = styled(BaseButton)`
  font-weight: 600;

  ${RawFeatherIcon} {
    margin-right: 0.5rem;

    @media (max-width: 360px) {
      display: none;
    }
  }
`;

export const StepButton = styled(BaseButton).attrs(() => ({
  color: "secondary",
}))`
  background-color: ${(props) => props.theme.secondary500};
  border-color: ${(props) => props.theme.secondary500};
  color: ${(props) => props.theme.white};
  font-size: 1.5rem;

  &:hover,
  &:focus,
  &:active {
    color: ${(props) => props.theme.white};
    background-color: ${(props) => props.theme.secondary600};
    border-color: ${(props) => props.theme.secondary600};
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    background-color: ${(props) => props.theme.secondary500};
    border-color: ${(props) => props.theme.secondary500};
    opacity: 0.5;
  }

  margin: 0 auto;
  width: 100%;
  max-width: 400px;
  height: 80px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4.5rem;

  & > span {
    font-weight: 400;
    font-size: 0.875rem;

    strong {
      font-weight: 600;
      font-size: 1.25rem;
    }
  }

  ${RawFeatherIcon} {
    position: absolute;
    right: 1.5rem;
  }
`;

export const SelectedButton = styled(Button).attrs(() => ({
  color: "primary",
}))`
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
    background-color: ${(props) => props.theme.primary500};
    border-color: ${(props) => props.theme.primary500};
    opacity: 0.5;
  }
`;

export const StyledButtonLabel = styled.label`
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) =>
    props.$empty ? props.theme.black50 : props.theme.primary500};
  opacity: ${(props) => (props.$disabled ? 0.5 : 1)};

  input {
    font-weight: inherit;
    border-radius: ${(props) => props.theme.borderRadius} 0 0
      ${(props) => props.theme.borderRadius};
    border: none;
    outline: none;
    display: block;
    width: 3rem;
    height: 2.25rem;
    text-align: right;
    -moz-appearance: textfield;

    &::-webkit-outer-spin-button,
    &::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }

    &,
    &[disabled] {
      background-color: white;
    }
  }

  &::after {
    display: flex;
    content: "€";
    background-color: white;
    height: 2.25rem;
    align-items: center;
    padding-right: 0.75rem;
    padding-left: 0.1rem;
    font-weight: inherit;
    border-radius: 0 ${(props) => props.theme.borderRadius}
      ${(props) => props.theme.borderRadius} 0;
  }
`;

export const Theme = ({ type, ...rest }) => (
  <ThemeProvider
    theme={CONFIG[type]?.theme || CONFIG.default.theme}
    {...rest}
  />
);

Theme.propTypes = {
  type: PropTypes.oneOf(Object.keys(CONFIG)),
};
