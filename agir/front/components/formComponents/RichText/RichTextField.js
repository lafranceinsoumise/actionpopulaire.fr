import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Editor from "./Editor";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledInput = styled.div``;
const StyledError = styled.span``;

const StyledField = styled.label`
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto auto auto;
  grid-gap: 4px 0.75rem;
  margin-bottom: 0;
  align-items: stretch;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1;

  ${StyledLabel} {
    grid-row: 1;
    grid-column: 1/3;
    font-weight: 600;
  }
  ${StyledHelpText} {
    grid-row: 2;
    grid-column: 1/3;
  }

  ${StyledInput} {
    grid-row: 3;
    grid-column: 1/3;
  }

  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    grid-row: 4;
    grid-column: 1/3;
    color: ${style.redNSP};
  }
`;

const RichTextField = (props) => {
  const {
    id,
    value = "",
    onChange,
    error,
    label,
    helpText,
    disabled,
    placeholder,
  } = props;

  return (
    <StyledField
      htmlFor={id}
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <StyledInput>
        <Editor
          id={id}
          disabled={disabled}
          onChange={onChange}
          value={value}
          hasError={!!error}
          placeholder={placeholder}
        />
      </StyledInput>
      <StyledError>{error}</StyledError>
    </StyledField>
  );
};

RichTextField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func,
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.node,
  error: PropTypes.string,
  disabled: PropTypes.bool,
  placeholder: PropTypes.string,
};

export default RichTextField;
