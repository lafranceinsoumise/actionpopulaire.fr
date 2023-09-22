import PropTypes from "prop-types";
import React, { forwardRef, useCallback, useMemo, useRef } from "react";
import { useDropArea } from "react-use";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "../genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span`
  color: ${(props) => props.theme.black700};
`;
const StyledError = styled.span`
  color: ${(props) => props.theme.redNSP};
`;
const StyledClearButton = styled.button``;
const StyledButtonWrapper = styled.span`
  display: inline-flex;
  flex-flow: row nowrap;
  width: auto;
  gap: ${(props) => (props.$empty ? 0 : 0.5)}rem;
  padding: 0 ${(props) => (props.$empty ? 0 : 0.5)}rem 0
    ${(props) => (props.$empty ? 0 : 1)}rem;
  border: 2px solid;
  border-color: ${({ $empty, $invalid, theme }) =>
    !$empty && $invalid ? theme.redNSP : "transparent"};
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${({ $empty, $invalid }) =>
    $empty
      ? "0px 0px 2px rgba(0, 0, 0, 0), 0px 3px 3px rgba(0, 35, 44, 0)"
      : $invalid
      ? "none"
      : "0px 0px 2px rgba(0, 0, 0, 0.5), 0px 3px 3px rgba(0, 35, 44, 0.1)"};
  overflow: hidden;
  max-width: 100%;

  ${Button} {
    flex: 1 1 auto;
    text-align: left;
    font-weight: 500;
    border: none;
  }

  ${StyledClearButton} {
    flex: 0 0 auto;
    width: ${(props) => (!props.$empty ? "auto" : 0)};
    opacity: ${(props) => (!props.$empty ? 1 : 0)};
    background-color: transparent;
    padding: 0 ${(props) => (!props.$empty ? 0.5 : 0)}rem;
    margin: 0;
    border: none;
    border-radius: 0;
    color: ${({ $invalid, theme }) =>
      $invalid ? theme.redNSP : theme.black500};
    display: flex;
    align-items: center;
    justify-content: start;
    cursor: ${(props) => (props.$disabled ? "default" : "pointer")};

    &:hover,
    &:focus {
      filter: brightness(0.8);
    }

    &:active {
      filter: brightness(0.9);
    }

    &[disabled],
    &:hover[disabled],
    &:focus[disabled] {
      opacity: ${(props) => (!props.$empty ? 0.7 : 0)};
      filter: none;
    }
  }
`;

const StyledField = styled.div`
  label {
    display: block;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    margin: 0;

    & > * {
      display: block;
      margin: 0;
    }

    ${StyledLabel} {
      font-weight: 600;
    }

    ${StyledButtonWrapper} {
      display: inline-flex;
      margin-top: 0.5rem;
      min-width: 1px;
    }

    input[type="file"] {
      display: none;
    }
  }
`;

const FileField = forwardRef((props, ref) => {
  const {
    id,
    name,
    value,
    onChange,
    error,
    label,
    helpText,
    disabled,
    ...rest
  } = props;

  const labelRef = useRef(null);
  const handleChange = useCallback(
    (e) => {
      const file =
        e?.target?.files && e.target.files[e.target.files.length - 1];
      file && onChange && onChange(file);
    },
    [onChange],
  );
  const handleDrop = useCallback(
    (files) => {
      const file = files && files[files.length - 1];
      file && onChange && onChange(file);
    },
    [onChange],
  );
  const handleClear = useCallback(() => {
    onChange && onChange(null);
  }, [onChange]);

  const [bond, dropState] = useDropArea({
    onFiles: handleDrop,
  });

  const handleClick = useCallback(() => {
    labelRef.current && labelRef.current.click();
  }, []);

  const fileName = useMemo(() => {
    if (value && typeof value === "string") {
      return value.split("/").pop();
    }
    if (value && value.name) {
      return value.name;
    }
    return "";
  }, [value]);

  return (
    <StyledField {...bond} $valid={!error} $invalid={!!error} $empty={!value}>
      <label htmlFor={id} ref={labelRef}>
        {label && <StyledLabel>{label}</StyledLabel>}
        {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
        {!!error && <StyledError>{error}</StyledError>}
        <input
          {...rest}
          ref={ref}
          id={id}
          name={name}
          type="file"
          onChange={handleChange}
          value=""
          disabled={disabled}
        />
        <StyledButtonWrapper
          $invalid={!!error}
          $empty={!fileName}
          $disabled={disabled}
          $dropping={dropState.over}
        >
          <Button
            link={!disabled && !!fileName}
            color={fileName ? "link" : !!error ? "danger" : "default"}
            type="button"
            title={fileName || "Parcourir"}
            icon={fileName ? "paperclip" : "upload"}
            onClick={!fileName ? handleClick : undefined}
            href={fileName || undefined}
            disabled={disabled}
            download={!!fileName}
          >
            {fileName || "Parcourir…"}
          </Button>
          <StyledClearButton
            type="button"
            disabled={!fileName || disabled}
            onClick={handleClear}
          >
            <RawFeatherIcon
              name="x-circle"
              width="2rem"
              height="2rem"
              strokeWidth="1.5"
            />
          </StyledClearButton>
        </StyledButtonWrapper>
      </label>
    </StyledField>
  );
});

FileField.propTypes = {
  value: PropTypes.any,
  name: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  id: PropTypes.string,
  label: PropTypes.node,
  helpText: PropTypes.node,
  error: PropTypes.node,
  disabled: PropTypes.bool,
};

FileField.displayName = "FileField";

export default FileField;
