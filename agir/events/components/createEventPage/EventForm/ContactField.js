import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import TextField from "@agir/front/formComponents/TextField";

const StyledDefaultField = styled.div`
  padding: 0.5rem 0.75rem;
  border: 1px solid ${style.black100};

  p {
    margin: 0;
    padding: 0;
    line-height: 1.5;
  }

  button {
    border-radius: 0;
    border: none;
    box-shadow: none;
    padding: 0;
    background-color: transparent;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    color: ${style.primary500};
    text-align: left;

    &[disabled],
    &[disabled]:hover {
      opacity: 0.5;
      cursor: default;
    }
  }
`;

const StyledField = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: repeat(4, auto);
  grid-gap: 1rem 0;
`;

const ContactField = (props) => {
  const { onChange, contact = {}, error, disabled, required } = props;
  const { name, email, phone, hidePhone, isDefault } = contact;

  const [isEditable, setIsEditable] = useState(false);
  const editDefaultContact = useCallback(() => {
    setIsEditable(true);
  }, []);

  const handleChange = useCallback(
    (e) => {
      onChange && onChange(props.name, e.target.name, e.target.value);
    },
    [props.name, onChange],
  );

  const handleChangeHidePhone = useCallback(
    (e) => {
      onChange && onChange(props.name, e.target.name, e.target.checked);
    },
    [props.name, onChange],
  );

  return (
    <StyledField>
      {!isEditable && name && email && phone && isDefault ? (
        <StyledDefaultField>
          <p>{name}</p>
          <p>{email}</p>
          <p>{phone}</p>
          <button onClick={editDefaultContact}>Modifier le contact</button>
        </StyledDefaultField>
      ) : (
        <>
          <TextField
            label="Nom de la personne à contacter"
            name="name"
            autoComplete="name"
            value={name}
            onChange={handleChange}
            disabled={disabled}
            required={required}
            error={error && error.name}
          />
          <TextField
            label="Adresse e-mail de contact"
            name="email"
            autoComplete="email"
            type="email"
            value={email}
            onChange={handleChange}
            disabled={disabled}
            required={required}
            error={error && error.email}
          />
          <PhoneField
            label="Numéro de téléphone de contact"
            helpText="Obligatoire pour que l’équipe de coordination puisse vous contacter mais peut être caché aux participant·e·s."
            name="phone"
            autoComplete="tel"
            value={phone}
            onChange={handleChange}
            disabled={disabled}
            required={required}
            error={error && error.phone}
          />
        </>
      )}
      <CheckboxField
        label="Cacher le numéro de téléphone"
        name="hidePhone"
        onChange={handleChangeHidePhone}
        disabled={disabled}
        value={hidePhone}
      />
    </StyledField>
  );
};
ContactField.propTypes = {
  onChange: PropTypes.func,
  value: PropTypes.string,
  name: PropTypes.string.isRequired,
  contact: PropTypes.shape({
    name: PropTypes.string,
    email: PropTypes.string,
    phone: PropTypes.string,
    hidePhone: PropTypes.bool,
  }),
  error: PropTypes.shape({
    name: PropTypes.string,
    email: PropTypes.string,
    phone: PropTypes.string,
  }),
  disabled: PropTypes.bool,
  required: PropTypes.bool,
};
export default ContactField;
