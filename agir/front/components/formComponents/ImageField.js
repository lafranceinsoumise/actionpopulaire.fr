import PropTypes from "prop-types";
import React, { forwardRef, useCallback, useMemo, useRef } from "react";

import Button from "@agir/front/genericComponents/Button";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledError = styled.span`
  color: ${style.redNSP};
`;

const StyledField = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;

  label {
    flex: 0 0 auto;
    display: flex;
    flex-flow: column nowrap;
    align-items: flex-start;
    font-size: 1rem;
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
      margin-top: 0.5rem;
    }
  }
`;

const ImageField = forwardRef((props, ref) => {
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

  const deleteImage = useCallback(() => {
    onChange(null);
  }, [onChange]);

  const handleClick = useCallback(() => {
    labelRef.current && labelRef.current.click();
  }, []);

  const thumbnail = useMemo(() => {
    if (typeof value === "string") {
      return value;
    }
    if (value && value.name) {
      return URL.createObjectURL(value);
    }

    return null;
  }, [value]);

  const imageName = useMemo(() => {
    if (value && typeof value === "string") {
      return value;
    }
    if (value && value.name) {
      return value.name;
    }
    return "";
  }, [value]);

  return (
    <>
      <StyledField $valid={!error} $invalid={!!error} $empty={!!value}>
        {imageName && (
          <img
            src={thumbnail}
            alt=""
            style={{
              maxWidth: "178px",
              maxHeight: "100px",
              marginRight: "1.5rem",
            }}
          />
        )}
        <label htmlFor={id} ref={labelRef}>
          {label && <StyledLabel>{label}</StyledLabel>}
          {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
          <input
            {...rest}
            disabled={disabled}
            ref={ref}
            id={id}
            name={name}
            type="file"
            onChange={handleChange}
            value=""
          />
          <Button type="button" wrap onClick={handleClick} disabled={disabled}>
            <RawFeatherIcon name="camera" style={{ marginRight: "0.5rem" }} />
            {imageName ? "Remplacer l'image" : "Ajouter une image"}
          </Button>
          {imageName && (
            <Button
              color="link"
              disabled={disabled}
              onClick={deleteImage}
              style={{ marginTop: 0 }}
            >
              Supprimer l'image
            </Button>
          )}
        </label>
      </StyledField>
      {!!error && <StyledError>{error}</StyledError>}
    </>
  );
});

ImageField.propTypes = {
  value: PropTypes.any,
  name: PropTypes.string,
  onChange: PropTypes.func,
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  error: PropTypes.string,
  disabled: PropTypes.bool,
};

ImageField.displayName = "ImageField";

export default ImageField;
