import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import CountryField from "@agir/front/formComponents/CountryField";
import TextField from "@agir/front/formComponents/TextField";

const StyledField = styled.div`
  display: grid;
  grid-template-columns: 160px 1fr 160px;
  grid-template-rows: repeat(4, auto);
  grid-auto-rows: auto;
  grid-gap: 1rem 0.5rem;

  @media (max-width: ${style.collapse}px) {
    grid-template-columns: 1fr;
  }

  & > * {
    grid-column: span 3;

    &:nth-child(4),
    &:nth-child(5),
    &:nth-child(6) {
      grid-column: span 1;
    }

    @media (max-width: ${style.collapse}px) {
      grid-column: span 1;
    }
  }

  button {
    display: inline-block;
    background: transparent;
    border: none;
    outline: none;
    cursor: pointer;
    padding: 0;
    margin: 0;
    font-size: 1rem;
    line-height: 1;
    font-weight: 400;
    width: auto;

    &[disabled],
    &[disabled]:hover {
      cursor: default;
    }

    @media (max-width: ${style.collapse}px) {
      text-align: left;
      line-height: 1.5;
    }
  }
`;

const LocationField = (props) => {
  const {
    onChange,
    location = {},
    error = {},
    help,
    disabled,
    required,
  } = props;
  const { name, address1, address2, city, zip, country } = location;

  const [hasAddress2, setHasAddress2] = useState(!!address2);

  const handleChange = useCallback(
    (e) => {
      onChange &&
        onChange(
          props.name,
          e.target.name,
          e.target.value.replace(/^\s+/g, ""),
        );
    },
    [props.name, onChange],
  );

  const handleChangeCountry = useCallback(
    (country) => {
      onChange && onChange(props.name, "country", country);
    },
    [props.name, onChange],
  );

  const displayAddress2 = useCallback(() => {
    setHasAddress2(true);
  }, []);

  useEffect(() => {
    !hasAddress2 && address2 && setHasAddress2(true);
  }, [hasAddress2, address2]);

  return (
    <StyledField>
      <TextField
        label="Nom du lieu"
        name="name"
        value={name}
        onChange={handleChange}
        required={required}
        disabled={disabled}
        error={error && error.name}
        helpText={help && help.name}
      />
      <TextField
        label="Adresse du lieu"
        autoComplete="address-line1"
        name="address1"
        value={address1}
        onChange={handleChange}
        required={required}
        disabled={disabled}
        error={error && error.address1}
        helpText={help && help.address1}
      />
      {hasAddress2 || address2 || error.address2 ? (
        <TextField
          label=""
          name="address2"
          autoComplete="address-line2"
          value={address2}
          onChange={handleChange}
          disabled={disabled}
          error={error && error.address2}
          helpText={help && help.address2}
        />
      ) : (
        <div style={{ paddingBottom: ".5rem" }}>
          <button type="button" onClick={displayAddress2} disabled={disabled}>
            + Ajouter une deuxième ligne pour l'adresse
          </button>
        </div>
      )}
      <TextField
        label="Code postal"
        name="zip"
        autoComplete="postal-code"
        value={zip}
        onChange={handleChange}
        required={required}
        disabled={disabled}
        error={error && error.zip}
        helpText={help && help.zip}
      />
      <TextField
        label="Commune"
        name="city"
        autoComplete="city"
        value={city}
        onChange={handleChange}
        required={required}
        disabled={disabled}
        error={error && error.city}
        helpText={help && help.city}
      />
      <CountryField
        label="Pays"
        name="country"
        autoComplete="country-name"
        placeholder=""
        value={country}
        onChange={handleChangeCountry}
        required={required}
        disabled={disabled}
        error={error && error.country}
        helpText={help && help.country}
      />
    </StyledField>
  );
};
LocationField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string,
  name: PropTypes.string.isRequired,
  location: PropTypes.shape({
    name: PropTypes.string,
    address1: PropTypes.string,
    address2: PropTypes.string,
    city: PropTypes.string,
    zip: PropTypes.string,
    country: PropTypes.string,
  }).isRequired,
  error: PropTypes.shape({
    name: PropTypes.string,
    address1: PropTypes.string,
    address2: PropTypes.string,
    city: PropTypes.string,
    zip: PropTypes.string,
    country: PropTypes.string,
  }),
  help: PropTypes.shape({
    name: PropTypes.string,
    address1: PropTypes.string,
    address2: PropTypes.string,
    city: PropTypes.string,
    zip: PropTypes.string,
    country: PropTypes.string,
  }),
  required: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default LocationField;
