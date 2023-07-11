import countries from "localized-countries/data/fr";

import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";

import SelectField from "@agir/front/formComponents/SelectField";

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

export const COUNTRIES = [...FIRST_COUNTRIES, ...OTHER_COUNTRIES];

const CountryField = (props) => {
  const { onChange, value, ...rest } = props;

  const handleChange = useCallback(
    (country) => {
      onChange && onChange(country && country.value);
    },
    [onChange],
  );

  const selectedCountry = useMemo(
    () => value && COUNTRIES.find((c) => c.value === value),
    [value],
  );

  return (
    <SelectField
      {...rest}
      isSearchable
      autoComplete="country-name"
      value={selectedCountry}
      options={COUNTRIES}
      onChange={handleChange}
    />
  );
};
CountryField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.oneOf(["", ...Object.keys(countries)]),
};
export default CountryField;
