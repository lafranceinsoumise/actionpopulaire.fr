import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { RawFeatherIcon as FeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledBox = styled.span``;
const StyledToggle = styled.span``;

const StyledField = styled.label`
  position: relative;
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  font-size: ${(props) => (props.$small ? "0.875rem" : "1rem")};
  line-height: 1.5;
  cursor: ${({ $disabled }) => ($disabled ? "default" : "pointer")};
  font-weight: 400;

  input {
    position: absolute;
    z-index: -1;
    opacity: 0;
  }

  ${StyledBox} {
    display: flex;
    justify-content: center;
    align-items: center;
    flex: 0 0 auto;
    margin-top: 0.25em;
    margin-right: 0.5em;
    width: ${(props) => (props.$small ? "0.875rem" : "1rem")};
    height: ${(props) => (props.$small ? "0.875rem" : "1rem")};
    border-radius: ${(props) => props.theme.softBorderRadius};
    border-style: solid;
    border-width: ${({ $checked }) => ($checked ? 0 : 1)}px;
    border-color: ${({ $disabled, theme }) =>
      $disabled ? theme.black200 : theme.black1000};
    background-color: ${({ $checked, $disabled, theme }) => {
      if ($checked && $disabled) {
        return theme.primary150;
      }
      if ($checked) {
        return theme.primary500;
      }
      if ($disabled) {
        return theme.black100;
      }
      return "transparent";
    }};
    transition: all 200ms ease-in;

    span {
      justify-content: center;
    }
  }

  input:focus + ${StyledBox} {
    box-shadow: ${({ $disabled, theme }) =>
      !$disabled ? `0 0 0 4px ${theme.primary100}` : "none"};
  }

  ${StyledToggle} {
    display: flex;
    flex-flow: column nowrap;
    align-items: stretch;
    justify-content: center;
    font-size: inherit;
    line-height: inherit;
    position: relative;
    height: 1.5em;
    margin-right: 0.5em;

    &::before,
    &::after {
      content: "";
      flex: 0 0 auto;
      display: block;
      transition: opacity background 200ms;
    }

    &::before {
      width: 2rem;
      height: 0.75rem;
      border-radius: 2.5rem;
      background: ${(props) => props.theme.primary100};
      background-color: ${({ $checked, theme }) =>
        $checked ? theme.primary100 : "transparent"};
      border: 1px solid;
      border-color: ${({ $checked, theme }) =>
        $checked ? theme.primary100 : theme.black100};
      opacity: ${({ $disabled }) => ($disabled ? 0.5 : 1)};
    }

    &::after {
      position: absolute;
      width: 1rem;
      height: 1rem;
      border-radius: 100%;
      background: ${(props) => props.theme.primary500};
      background-color: ${({ $checked, $disabled, theme }) => {
        if ($checked && $disabled) {
          return theme.primary150;
        }
        if ($checked) {
          return theme.primary500;
        }
        if ($disabled) {
          return theme.black100;
        }

        return theme.black200;
      }};
      align-self: ${({ $checked }) => ($checked ? "end" : "start")};
    }
  }

  input:focus + ${StyledToggle}::after {
    box-shadow: ${({ $checked, $disabled, theme }) =>
      !$disabled
        ? `0 0 0 3px ${$checked ? theme.primary150 : theme.primary100}`
        : "none"};
  }

  ${StyledLabel} {
    flex: 1 1 auto;
    font-weight: inherit;
    color: ${({ $disabled, theme }) =>
      $disabled ? theme.black500 : theme.black1000};

    &::first-letter {
      text-transform: uppercase;
    }
  }
`;

const CheckboxField = (props) => {
  const {
    id,
    onChange,
    value = false,
    inputValue,
    label,
    className,
    style,
    small,
    toggle = false,
    ...rest
  } = props;

  return (
    <StyledField
      style={style}
      className={className}
      htmlFor={id}
      $checked={!!value}
      $disabled={rest.disabled}
      $small={small}
    >
      <input
        {...rest}
        type="checkbox"
        id={id}
        onChange={onChange}
        checked={!!value}
        value={inputValue}
      />
      {toggle ? (
        <StyledToggle aria-hidden />
      ) : (
        <StyledBox aria-hidden>
          {!!value && (
            <FeatherIcon
              name="check"
              color="white"
              strokeWidth={4}
              width="12px"
              height="12px"
            />
          )}
        </StyledBox>
      )}
      {label && <StyledLabel>{label}</StyledLabel>}
    </StyledField>
  );
};

CheckboxField.propTypes = {
  value: PropTypes.bool,
  onChange: PropTypes.func,
  id: PropTypes.string,
  label: PropTypes.node,
  disabled: PropTypes.bool,
  style: PropTypes.object,
  className: PropTypes.string,
  inputValue: PropTypes.string,
  small: PropTypes.bool,
  toggle: PropTypes.bool,
};

export default CheckboxField;
