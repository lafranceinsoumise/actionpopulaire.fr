import PropTypes from "prop-types";
import React, { useLayoutEffect, useRef } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledInput = styled.input``;
const StyledTextArea = styled.textarea``;
const StyledIcon = styled.span``;
const StyledCounter = styled.span`
  color: ${({ $invalid }) => ($invalid ? style.redNSP : "inherit")};
`;
const StyledError = styled.span``;

const StyledField = styled.label`
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto auto auto;
  grid-gap: 0 0.75rem;
  align-items: stretch;
  font-size: 0.813rem;
  font-weight: 400;
  line-height: 1;

  & > * {
    margin: 4px 0;
  }

  ${StyledLabel} {
    grid-row: 1;
    grid-column: 1/3;
    font-weight: 600;
  }
  ${StyledHelpText} {
    grid-row: 2;
    grid-column: 1/3;
  }

  ${StyledInput}, ${StyledTextArea} {
    grid-row: 3;
    grid-column: 1/3;
    border-radius: 0;
    border: 1px solid;
    border-color: ${({ $invalid }) =>
      $invalid ? style.redNSP : style.black100};
    max-width: 100%;
    padding: 0.5rem;
    padding-right: ${({ $invalid }) => ($invalid ? "3.25rem" : "0.5rem")};

    &:focus {
      border-color: ${({ $invalid }) =>
        $invalid ? style.redNSP : style.black1000};
    }
  }
  ${StyledInput} {
    height: 40px;
    font-size: 1rem;

    @media (max-width: ${style.collapse}px) {
      font-size: 0.875rem;
    }
  }
  ${StyledTextArea} {
    resize: none;
    line-height: 1.5;
  }
  ${StyledIcon} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    grid-row: 3;
    grid-column: 2/3;
    align-items: flex-start;
    justify-content: flex-end;
    padding: 0.5rem;
    color: ${style.redNSP};
  }
  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    grid-row: 4;
    grid-column: 1/3;
    color: ${style.redNSP};
  }
  ${StyledCounter} {
    grid-row: 4;
    grid-column: 2/3;
    text-align: right;
  }
`;

const TextField = (props) => {
  const {
    id,
    type,
    onChange,
    value,
    error,
    label,
    helpText,
    maxLength,
    textArea,
    ...rest
  } = props;

  const textAreaRef = useRef(null);
  useLayoutEffect(() => {
    if (value && textAreaRef.current) {
      textAreaRef.current.style.height = "inherit";
      textAreaRef.current.style.height =
        textAreaRef.current.scrollHeight + 4 + "px";
    }
  }, [value]);

  return (
    <StyledField
      htmlFor={id}
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      {textArea ? (
        <StyledTextArea
          {...rest}
          ref={textAreaRef}
          id={id}
          type={type}
          onChange={onChange}
          value={value}
          rows={1}
        />
      ) : (
        <StyledInput
          {...rest}
          id={id}
          type={type}
          onChange={onChange}
          value={value}
        />
      )}
      <StyledIcon>
        <FeatherIcon name="alert-circle" />
      </StyledIcon>
      <StyledError>{error}</StyledError>
      {typeof maxLength === "number" ? (
        <StyledCounter $invalid={!!error || value.length > maxLength}>
          {value.length}/{maxLength}
        </StyledCounter>
      ) : null}
    </StyledField>
  );
};

TextField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  type: PropTypes.oneOf(["text", "email", "password"]),
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  error: PropTypes.string,
  maxLength: PropTypes.number,
  textArea: PropTypes.bool,
};

TextField.defaultProps = {
  type: "text",
  textArea: false,
};

export default TextField;
