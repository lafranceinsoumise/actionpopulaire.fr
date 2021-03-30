import React, { useState } from "react";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import TextField from "@agir/front/formComponents/TextField";
import styled from "styled-components";

const StyledField = styled.div`
  span:first-child {
    font-size: 0.813rem;
    font-weight: 600;
    line-height: 1;
    padding: 4px 0;
  }
`;

const VisioConferenceField = (props) => {
  const {
    id,
    name,
    label,
    placeholder,
    value,
    defaultUrl,
    onChange,
    error,
    disabled,
    ...rest
  } = props;

  const [isVisio, setIsVisio] = useState(!!value);

  const handleChange = (e) => {
    onChange(name, e.target.value);
  };

  const handleChangeUrl = (event) => {
    if (!event.target.checked) {
      onChange(name, "");
      return;
    }
    onChange(name, defaultUrl);
  };

  const handleChangeVisio = (event) => {
    setIsVisio(event.target.checked);
    if (!event.target.checked) {
      onChange(name, "");
      return;
    }
  };

  return (
    <StyledField>
      <span>{label}</span>
      <CheckboxField
        disabled={disabled}
        label="Se déroule en ligne"
        value={isVisio}
        onChange={handleChangeVisio}
      />
      {isVisio && (
        <>
          {!!defaultUrl && (
            <CheckboxField
              disabled={disabled}
              label="Utiliser le service de visio-conférence automatique de La France insoumise"
              value={value === defaultUrl}
              onChange={handleChangeUrl}
            />
          )}
          <TextField
            {...rest}
            label=""
            disabled={disabled}
            name="url"
            error={error}
            value={value}
            onChange={handleChange}
            placeholder={placeholder}
          />
        </>
      )}
    </StyledField>
  );
};

export default VisioConferenceField;
