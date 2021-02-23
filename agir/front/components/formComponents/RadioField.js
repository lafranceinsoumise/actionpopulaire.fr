import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

const StyledOptionLabel = styled.span``;
const StyledBox = styled.span``;

const StyledOption = styled.label`
  position: relative;
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  font-size: 0.875rem;
  line-height: 1.5;
  cursor: ${({ $disabled }) => ($disabled ? "default" : "pointer")};

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
    margin-top: 0.15rem;
    margin-right: 0.5rem;
    width: 1rem;
    height: 1rem;
    border-radius: 100%;
    border-style: solid;
    border-width: 1px;
    border-color: ${({ $checked, $disabled }) => {
      if ($checked && $disabled) {
        return style.primary150;
      }
      if ($checked) {
        return style.primary500;
      }
      if ($disabled) {
        return style.black200;
      }
      return style.black1000;
    }};
    background: ${({ $checked, $disabled }) => {
      if ($checked && $disabled) {
        return `radial-gradient(circle, ${style.primary150} 4px, ${style.white} 5px, ${style.white} 6px, ${style.primary150} 7px)`;
      }
      if ($checked) {
        return `radial-gradient(circle, ${style.primary500} 4px, ${style.white} 5px, ${style.white} 6px, ${style.primary500} 7px)`;
      }
      if ($disabled) {
        return style.black100;
      }
      return style.white;
    }};
    transition: all 200ms ease-in;
  }

  input:focus + ${StyledBox}, &:hover ${StyledBox} {
    ${({ $checked, $disabled }) =>
      !$disabled
        ? $checked
          ? "opacity: .5;"
          : `background: ${style.black50};`
        : ""};
  }

  ${StyledOptionLabel} {
    flex: 1 1 auto;
    font-weight: 400;
    color: ${({ $disabled }) => ($disabled ? style.black500 : style.black1000)};
  }
`;

const StyledLabel = styled.div``;
const StyledHelpText = styled.div``;
const StyledOptions = styled.div``;
const StyledError = styled.div``;

const StyledField = styled.div`
  display: grid;
  align-items: stretch;
  font-size: 0.813rem;
  font-weight: 400;
  line-height: 1;

  & > * {
    margin: 4px 0;
  }

  ${StyledLabel} {
    font-weight: 600;
  }

  ${StyledHelpText} {
    line-height: 1.5;
  }

  ${StyledOptions} {
    display: grid;
    grid-gap: 0.25rem;
  }

  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    color: ${style.redNSP};
  }
`;

const RadioField = (props) => {
  const {
    id,
    onChange,
    value,
    options,
    label,
    error,
    helpText,
    disabled,
    ...rest
  } = props;

  const handleChange = useCallback(
    (e) => {
      onChange(e.target.value);
    },
    [onChange]
  );

  return (
    <StyledField $valid={!error} $invalid={!!error} $empty={!!value}>
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <StyledError>{error}</StyledError>
      <StyledOptions id={id}>
        {options.map((option) => (
          <StyledOption
            key={option.value}
            htmlFor={option.value}
            $checked={value === option.value}
            $disabled={disabled}
          >
            <input
              {...rest}
              id={option.value}
              type="radio"
              onChange={handleChange}
              checked={value === option.value}
              value={option.value}
            />
            <StyledBox />
            <StyledOptionLabel>{option.label}</StyledOptionLabel>
          </StyledOption>
        ))}
      </StyledOptions>
    </StyledField>
  );
};

RadioField.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      label: PropTypes.string,
    })
  ).isRequired,
  id: PropTypes.string,
  name: PropTypes.string,
  label: PropTypes.node,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  helpText: PropTypes.string,
};

export default RadioField;
