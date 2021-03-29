import PropTypes from "prop-types";
import React, { forwardRef } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledError = styled.span``;

const StyledField = styled.div`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;

  label {
    flex: 0 0 auto;
    display: flex;
    flex-flow: column nowrap;
    align-items: flex-start;
    font-size: 0.813rem;
    font-weight: 400;
    line-height: 1.5;

    & > * {
      margin: 0;
    }

    ${StyledLabel} {
      font-weight: 600;
    }

    input[type="file"] {
      display: none;
    }

    ${Button} {
      width: auto;
      margin-top: 0.5rem;
    }

    ${StyledError} {
      display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
      color: ${style.redNSP};
    }
  }
`;

const ImageField = forwardRef((props, ref) => {
  const { id, onChange, value, error, label, helpText, ...rest } = props;

  const labelRef = React.useRef(null);
  const handleChange = React.useCallback(
    (e) => {
      e &&
        e.target &&
        e.target.files &&
        onChange &&
        onChange(e.target.files[e.target.files.length - 1]);
    },
    [onChange]
  );

  const handleClick = React.useCallback(() => {
    labelRef.current && labelRef.current.click();
  }, []);

  /*
  const thumbnail = React.useMemo(() => {
    if (typeof value === "string") {
      return value;
    }
    if (value && value.name) {
      return URL.createObjectURL(value);
    }

    return null;
  }, [value]);
  */

  const imageName = React.useMemo(() => {
    if (typeof value === "string") {
      return value;
    }
    if (value && value.name) {
      return value.name;
    }

    return "";
  }, [value]);

  return (
    <StyledField $valid={!error} $invalid={!!error} $empty={!!value}>
      <label htmlFor={id} ref={labelRef}>
        {label && <StyledLabel>{label}</StyledLabel>}
        {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
        <input
          {...rest}
          ref={ref}
          id={id}
          type="file"
          onChange={handleChange}
        />
        <Button
          color={imageName ? "primary" : "default"}
          type="button"
          small
          inline
          onClick={handleClick}
        >
          {imageName || "Ajouter une image"}
        </Button>
        <StyledError>{error}</StyledError>
      </label>
    </StyledField>
  );
});

ImageField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  error: PropTypes.string,
};

ImageField.displayName = "ImageField";

export default ImageField;
