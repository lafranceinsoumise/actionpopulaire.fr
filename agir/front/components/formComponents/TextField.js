import PropTypes from "prop-types";
import React, { forwardRef, useLayoutEffect, useRef } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { mergeRefs } from "@agir/lib/utils/react";

import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledIcon = styled(RawFeatherIcon)``;
const StyledInput = styled.input``;
const StyledTextArea = styled.textarea``;
const StyledErrorIcon = styled.span``;
const StyledCounter = styled.span`
  color: ${({ $invalid }) => ($invalid ? style.redNSP : "inherit")};
`;
const StyledError = styled.span``;

const StyledField = styled.label`
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto auto auto;
  grid-gap: 4px 0.75rem;
  align-items: stretch;
  font-size: ${({ $small }) => ($small ? "0.875rem" : "1rem")};
  font-weight: 400;
  line-height: 1;
  margin-bottom: 0;

  ${StyledLabel} {
    grid-row: 1;
    grid-column: 1/3;
    font-weight: 600;
  }
  ${StyledHelpText} {
    grid-row: 2;
    grid-column: 1/3;
    line-height: 1.5;
  }

  ${StyledIcon} {
    grid-row: 3;
    grid-column: 1/1;
    width: 3rem;
    margin-top: 0.5rem;
    align-items: start;
    justify-content: center;
    color: ${({ $invalid }) => ($invalid ? style.redNSP : style.black500)};
  }

  ${StyledInput}, ${StyledTextArea} {
    grid-row: 3;
    grid-column: 1/3;
    border-radius: ${style.softBorderRadius};
    border: 1px solid;
    border-color: ${({ $invalid }) =>
      $invalid ? style.redNSP : style.black100};
    max-width: 100%;
    padding: 0.5rem;
    padding-left: ${({ $icon }) => ($icon ? "3rem" : "0.5rem")};
    padding-right: ${({ $invalid }) => ($invalid ? "3rem" : "0.5rem")};
    background-color: ${({ $dark }) =>
      $dark ? style.black100 : "transparent"};

    &:focus {
      outline: none;
      border-color: ${({ $invalid, $dark }) =>
        $invalid ? style.redNSP : $dark ? style.black200 : style.black500};
    }
  }
  ${StyledInput} {
    height: 40px;
    font-size: ${({ $small }) => ($small ? "0.875rem" : "1rem")};
  }
  ${StyledTextArea} {
    resize: none;
    line-height: 1.5;
  }
  ${StyledErrorIcon} {
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
    grid-column: ${({ $hasCounter }) => ($hasCounter ? "1/2" : "1/3")};
    color: ${style.redNSP};
  }
  ${StyledCounter} {
    grid-row: 4;
    grid-column: 2/3;
    text-align: right;
    line-height: 1.5;
    font-size: 0.875em;
  }
`;

const TextField = forwardRef((props, ref) => {
  const {
    id,
    type,
    onChange,
    value = "",
    error,
    label,
    helpText,
    maxLength,
    textArea,
    rows,
    hasCounter,
    autoComplete,
    small,
    dark,
    icon,
    ...rest
  } = props;

  const textAreaRef = useRef(null);
  useLayoutEffect(() => {
    const textArea = textAreaRef.current;
    if (value && textArea) {
      textArea.style.height = textArea.scrollHeight + 4 + "px";
    }
    return () => {
      if (textArea) {
        textArea.style.height = "inherit";
      }
    };
  }, [value]);

  return (
    <StyledField
      htmlFor={id}
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
      $hasCounter={!!maxLength && !!hasCounter}
      $small={!!small}
      $dark={!!dark}
      $icon={!!icon}
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      {icon && <StyledIcon name={icon} />}
      {textArea ? (
        <StyledTextArea
          {...rest}
          ref={mergeRefs(ref, textAreaRef)}
          id={id}
          type={type}
          onChange={onChange}
          value={value}
          rows={rows || 1}
        />
      ) : (
        <StyledInput
          {...rest}
          ref={ref}
          id={id}
          type={type}
          onChange={onChange}
          value={value}
          autoComplete={autoComplete}
        />
      )}
      <StyledErrorIcon>
        <FeatherIcon name="alert-circle" />
      </StyledErrorIcon>
      <StyledError>{error}</StyledError>
      {hasCounter && typeof maxLength === "number" ? (
        <StyledCounter $invalid={!!error || value.length > maxLength}>
          {value.length}/{maxLength}
        </StyledCounter>
      ) : null}
    </StyledField>
  );
});

TextField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  type: PropTypes.oneOf(["text", "email", "password"]),
  id: PropTypes.string,
  label: PropTypes.node,
  helpText: PropTypes.node,
  error: PropTypes.string,
  maxLength: PropTypes.number,
  textArea: PropTypes.bool,
  rows: PropTypes.number,
  hasCounter: PropTypes.bool,
  autoComplete: PropTypes.string,
  small: PropTypes.bool,
  dark: PropTypes.bool,
  icon: PropTypes.string,
};

TextField.defaultProps = {
  type: "text",
  textArea: false,
  hasCounter: true,
  autoComplete: "on",
  small: false,
};

TextField.displayName = "TextField";

export default TextField;
