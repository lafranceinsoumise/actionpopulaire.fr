import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveSpan } from "@agir/front/genericComponents/grid";

const StyledOptionLabel = styled(ResponsiveSpan)``;
const StyledOption = styled.label`
  display: inline-flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  border-radius: ${(props) => props.theme.softBorderRadius};
  margin: 0;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 400;
  line-height: ${(props) => (props.$small ? 1.2 : 1.7)};
  min-height: ${(props) => (props.$small ? 2 : 2.5)}rem;
  gap: 0.5rem;
  border: 1px solid;
  border-color: ${(props) =>
    props.$disabled ? props.theme.text50 : props.theme.text200};
  cursor: ${(props) => (props.$disabled ? "default" : "pointer")};
  color: ${(props) =>
    props.$disabled ? props.theme.text500 : props.theme.text1000};
  background-color: ${(props) =>
    props.$disabled ? props.theme.text50 : "transparent"};

  transition: background-color 200ms;

  ${RawFeatherIcon} {
    color: ${(props) => props.theme.success500};
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
  gap: 0.5rem;
  margin-bottom: 0;

  ${StyledLabel} {
    font-weight: 600;
  }

  ${StyledHelpText} {
    line-height: 1.5;
  }

  ${StyledOptions} {
    margin-top: 0.5rem;
    display: flex;
    flex-flow: row wrap;
    grid-gap: 0.5rem;

    input {
      position: absolute;
      z-index: -1;
      opacity: 0;
    }

    input:focus + ${StyledOption} {
      border-color: ${(props) => props.theme.text500};
    }
  }

  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    color: ${(props) => props.theme.error500};
  }
`;

const RadioListField = (props) => {
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
          <React.Fragment key={option.value}>
            <input
              {...rest}
              id={id + "_" + option.value}
              type="radio"
              onChange={handleChange}
              checked={value === option.value}
              value={option.value}
              disabled={disabled}
            />
            <StyledOption
              key={option.value}
              htmlFor={id + "_" + option.value}
              $checked={value === option.value}
              $disabled={disabled}
              $small={small}
              type="button"
            >
              {value === option.value && (
                <RawFeatherIcon
                  name="check"
                  width={small ? "1rem" : "1.5rem"}
                  height={small ? "1rem" : "1.5rem"}
                  strokeWidth={1.33}
                />
              )}
              <StyledOptionLabel
                small={option.smallLabel || option.label}
                large={option.label}
              />
            </StyledOption>
          </React.Fragment>
        ))}
      </StyledOptions>
    </StyledField>
  );
};

RadioListField.propTypes = {
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

export default RadioListField;
