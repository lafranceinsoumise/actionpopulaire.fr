import PropTypes from "prop-types";
import React, { forwardRef, useCallback, useMemo, useRef } from "react";

import Button from "@agir/front/genericComponents/Button";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span`
  color: ${style.black700};
`;
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
      text-align: left;
    }
  }
`;

const FileField = forwardRef((props, ref) => {
  const { id, name, value, onChange, error, label, helpText, ...rest } = props;

  const labelRef = useRef(null);
  const handleChange = useCallback(
    (e) => {
      const file =
        e?.target?.files && e.target.files[e.target.files.length - 1];
      file && onChange && onChange(file);
    },
    [onChange]
  );

  const handleClick = useCallback(() => {
    labelRef.current && labelRef.current.click();
  }, []);

  const fileName = useMemo(() => {
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
        <label htmlFor={id} ref={labelRef}>
          {label && <StyledLabel>{label}</StyledLabel>}
          {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
          <input
            {...rest}
            ref={ref}
            id={id}
            name={name}
            type="file"
            onChange={handleChange}
            value=""
          />
          <Button
            color={error ? "danger" : fileName ? "primary" : "default"}
            type="button"
            wrap
            onClick={handleClick}
            title={fileName ? "Remplacer le document" : "Ajouter un document"}
          >
            <RawFeatherIcon
              name={fileName ? "file-text" : "upload"}
              style={{ marginRight: "0.5rem" }}
            />
            {fileName || "Ajouter un document"}
          </Button>
        </label>
      </StyledField>
      {!!error && <StyledError>{error}</StyledError>}
    </>
  );
});

FileField.propTypes = {
  value: PropTypes.any,
  name: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  error: PropTypes.string,
};

FileField.displayName = "FileField";

export default FileField;
