import countries from "localized-countries/data/fr";
import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import SelectField from "@agir/front/formComponents/SelectField";
import TextField from "@agir/front/formComponents/TextField";

const FIRST_COUNTRY_CODES = ["FR", "PT", "DZ", "MA", "TR", "IT", "GB", "ES"];
const FIRST_COUNTRIES = FIRST_COUNTRY_CODES.map((countryCode) => ({
  value: countryCode,
  label: countries[countryCode],
}));
const OTHER_COUNTRIES = Object.keys(countries)
  .map((countryCode) => {
    if (!FIRST_COUNTRY_CODES.includes(countryCode)) {
      return {
        value: countryCode,
        label: countries[countryCode],
      };
    }
  })
  .filter(Boolean)
  .sort(({ label: label1 }, { label: label2 }) => label1.localeCompare(label2));

const COUNTRIES = [...FIRST_COUNTRIES, ...OTHER_COUNTRIES];

const StyledField = styled.div`
  display: grid;
  grid-template-columns: 140px 1fr;
  grid-template-rows: repeat(6, auto);
  grid-gap: 0 0.5rem;

  & > * {
    grid-column: span 2;

    &:nth-child(4),
    &:nth-child(5) {
      grid-column: span 1;

      @media (max-width: ${style.collapse}px) {
        grid-column: span 2;
      }
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
    font-size: 0.813rem;
    line-height: 1;
    font-weight: 400;
    width: auto;

    &[disabled],
    &[disabled]:hover {
      cursor: default;
    }
  }
`;

const LocationField = (props) => {
  const { onChange, location = {}, error = {}, disabled, required } = props;
  const { name, address1, address2, city, zip, country } = location;

  const [hasAddress2, setHasAddress2] = useState(!!address2);

  const handleChange = useCallback(
    (e) => {
      onChange &&
        onChange(props.name, {
          ...location,
          [e.target.name]: e.target.value,
        });
    },
    [location, props.name, onChange]
  );

  const handleChangeCountry = useCallback(
    (country) => {
      onChange &&
        onChange(props.name, {
          ...location,
          country: country && country.value,
        });
    },
    [location, props.name, onChange]
  );

  useEffect(() => {
    !country && handleChangeCountry(COUNTRIES[0]);
  }, [country, handleChangeCountry]);

  const selectedCountry = useMemo(
    () =>
      location.country &&
      COUNTRIES.find((country) => country.value === location.country),
    [location.country]
  );

  const displayAddress2 = useCallback(() => {
    setHasAddress2(true);
  }, []);

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
      />
      <TextField
        label="Adresse du lieu"
        autocomplete="address-line1"
        name="address1"
        value={address1}
        onChange={handleChange}
        required={required}
        disabled={disabled}
        error={error && error.address1}
      />
      {hasAddress2 || address2 || error.address2 ? (
        <TextField
          label=""
          name="address2"
          autocomplete="address-line2"
          value={address2}
          onChange={handleChange}
          disabled={disabled}
          error={error && error.address2}
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
        autocomplete="postal-code"
        value={zip}
        onChange={handleChange}
        required={required}
        disabled={disabled}
        error={error && error.zip}
      />
      <TextField
        label="Ville"
        name="city"
        autocomplete="city"
        value={city}
        onChange={handleChange}
        required={required}
        disabled={disabled}
        error={error && error.city}
      />
      <SelectField
        label="Pays"
        name="country"
        autocomplete="country-name"
        placeholder=""
        value={selectedCountry}
        options={COUNTRIES}
        onChange={handleChangeCountry}
        required={required}
        disabled={disabled}
        error={error && error.country}
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
  required: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default LocationField;
