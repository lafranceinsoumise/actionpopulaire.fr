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
      $disabled ? theme.text200 : theme.text1000};
    background-color: ${({ $checked, $disabled, theme }) => {
      if ($checked && $disabled) {
        return theme.primary150;
      }
      if ($checked) {
        return theme.primary500;
      }
      if ($disabled) {
        return theme.text100;
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
    display: grid;
    grid-template-columns: 1rem 1rem;
    align-items: center;
    font-size: inherit;
    line-height: inherit;
    position: relative;
    height: 1.5em;
    margin-right: 0.5em;

    &::before,
    &::after {
      content: "";
      display: block;
      width: 100%;
      transition: opacity background 200ms;
    }

    &::before {
      grid-column: span 2;
      height: 0.5rem;
      border-radius: 2.5rem;
      background: ${(props) => props.theme.primary100};
      background-color: ${({ $checked, theme }) =>
        $checked ? theme.primary100 : "transparent"};
      border: 1px solid;
      border-color: ${({ $checked, theme }) =>
        $checked ? theme.primary100 : theme.text100};
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
          return theme.text100;
        }

        return theme.text200;
      }};
      grid-column: ${({ $checked }) => ($checked ? "2/3" : "1/2")};
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
      $disabled ? theme.text500 : theme.text1000};

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
