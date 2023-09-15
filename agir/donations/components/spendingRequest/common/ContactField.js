import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import PhoneField from "@agir/front/formComponents/PhoneField";
import TextField from "@agir/front/formComponents/TextField";

const StyledField = styled.div`
  display: flex;
  flex-flow: row nowrap;
  align-items: start;
  gap: 1rem;

  & > * {
    flex: 1 1 auto;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: column;
  }
`;

const ContactField = (props) => {
  const { onChange, value = {}, error, disabled, required } = props;
  const { name, phone } = value;

  const handleChange = useCallback(
    (e) => {
      onChange && onChange(props.name, e.target.name, e.target.value);
    },
    [props.name, onChange],
  );

  return (
    <StyledField>
      <TextField
        label={`Contact lié à la dépense ${
          required ? "(obligatoire)" : ""
        }`.trim()}
        name="name"
        autoComplete="name"
        value={name}
        onChange={handleChange}
        disabled={disabled}
        required={required}
        error={error && error.name}
        maxLength={255}
        hasCounter={false}
      />
      <PhoneField
        label={`Numéro de téléphone ${required ? "(obligatoire)" : ""}`.trim()}
        name="phone"
        autoComplete="tel"
        value={phone}
        onChange={handleChange}
        disabled={disabled}
        required={required}
        error={error && error.phone}
      />
    </StyledField>
  );
};
ContactField.propTypes = {
  onChange: PropTypes.func,
  name: PropTypes.string.isRequired,
  value: PropTypes.shape({
    name: PropTypes.string,
    phone: PropTypes.string,
  }),
  error: PropTypes.shape({
    name: PropTypes.string,
    phone: PropTypes.string,
  }),
  disabled: PropTypes.bool,
  required: PropTypes.bool,
};
export default ContactField;
