import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

const StyledOptionLabel = styled.span``;
const StyledBox = styled.span``;

const StyledOption = styled.label`
  position: relative;
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  font-size: ${({ $small }) => ($small ? "0.875rem" : "1rem")};
  line-height: 1.5;
  cursor: ${({ $disabled }) => ($disabled ? "default" : "pointer")};
  margin-bottom: 0;

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
    margin-top: 0.25rem;
    margin-right: 0.5rem;
    width: 1rem;
    height: 1rem;
    border-radius: 100%;
    border-style: solid;
    border-width: 1px;
    border-color: ${(props) => {
      if (props.$checked && props.$disabled) {
        return props.theme.primary150;
      }
      if (props.$checked) {
        return props.theme.primary500;
      }
      if (props.$disabled) {
        return props.theme.black200;
      }
      return props.theme.black1000;
    }};
    background: ${(props) => {
      if (props.$checked && props.$disabled) {
        return `radial-gradient(circle, ${props.theme.primary150} 4px, ${props.theme.white} 5px, ${props.theme.white} 6px, ${props.theme.primary150} 7px)`;
      }
      if (props.$checked) {
        return `radial-gradient(circle, ${props.theme.primary500} 4px, ${props.theme.white} 5px, ${props.theme.white} 6px, ${props.theme.primary500} 7px)`;
      }
      if (props.$disabled) {
        return props.theme.black100;
      }
      return props.theme.white;
    }};
    transition: all 100ms ease-in;
  }

  &:hover ${StyledBox} {
    ${({ $checked, $disabled }) =>
      !$disabled && !$checked
        ? `background: ${(props) => props.theme.black50};`
        : ""};
  }

  input:focus + ${StyledBox} {
    box-shadow: ${(props) =>
      !props.$disabled ? `0 0 0 4px ${props.theme.primary100}` : "none"};
  }

  ${StyledOptionLabel} {
    padding-top: ${({ $small }) => ($small ? ".1rem" : "0")};
    flex: 1 1 auto;
    font-weight: 400;
    color: ${(props) =>
      props.$disabled ? props.theme.black500 : props.theme.black1000};
  }
`;

const StyledLabel = styled.div``;
const StyledHelpText = styled.div``;
const StyledOptions = styled.div``;
const StyledError = styled.div``;

const StyledField = styled.div`
  display: grid;
  align-items: stretch;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1;
  grid-gap: 4px 0;
  margin-bottom: 0;

  ${StyledLabel} {
    font-weight: 600;
  }

  ${StyledHelpText} {
    line-height: 1.5;
  }

  ${StyledOptions} {
    margin-top: 0.5rem;
    display: grid;
    grid-gap: 0.25rem;
  }

  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    color: ${(props) => props.theme.redNSP};
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
    small,
    ...rest
  } = props;

  const handleChange = useCallback(
    (e) => {
      onChange(e.target.value);
    },
    [onChange],
  );

  return (
    <StyledField
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
      tabIndex="1"
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <StyledError>{error}</StyledError>
      <StyledOptions id={id}>
        {options.map((option) => (
          <StyledOption
            key={option.value}
            htmlFor={id + "_" + option.value}
            $checked={value === option.value}
            $disabled={disabled}
            $small={small}
          >
            <input
              {...rest}
              id={id + "_" + option.value}
              type="radio"
              onChange={handleChange}
              checked={value === option.value}
              value={option.value}
              disabled={disabled}
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
  onChange: PropTypes.func,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      label: PropTypes.node,
    }),
  ).isRequired,
  id: PropTypes.string,
  name: PropTypes.string,
  label: PropTypes.node,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  helpText: PropTypes.node,
  small: PropTypes.bool,
};

export default RadioField;
