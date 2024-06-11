import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";

import SelectField from "@agir/front/formComponents/SelectField";

import ABROAD_POLLING_STATIONS from "./abroadPollingStations";

const ABROAD_POLLING_STATION_OPTIONS = ABROAD_POLLING_STATIONS.map(
  ({ country, list, pollingStation, countryCodes }) => {
    const value = `${pollingStation} / ${list} (${country})`;
    return {
      label: value,
      value: value,
      countryCodes,
    };
  },
);

const sortOptionsByCountries = (countries) => {
  if (Array.isArray(countries) && countries.length > 0) {
    return ABROAD_POLLING_STATION_OPTIONS.reduce((arr, option) => {
      if (
        Array.isArray(option.countryCodes) &&
        option.countryCodes.length > 0 &&
        option.countryCodes.some((country) => countries.includes(country))
      ) {
        arr.unshift(option);
      } else {
        arr.push(option);
      }
      return arr;
    }, []);
  }
  return ABROAD_POLLING_STATION_OPTIONS;
};

const AbroadPollingStationField = (props) => {
  const { value, name, onChange, countries } = props;
  const [selected, setSelected] = useState(
    ABROAD_POLLING_STATION_OPTIONS.find((option) => option.value === value),
  );
  const options = useMemo(() => sortOptionsByCountries(countries), [countries]);

  const handleChange = useCallback((pollingStation) => {
    setSelected(pollingStation);
  }, []);

  useEffect(() => {
    onChange({
      target: {
        name,
        value: selected?.value || "",
      },
    });
  }, [name, onChange, selected]);

  return (
    <SelectField
      {...props}
      placeholder="Chercher un bureau de vote"
      value={selected}
      options={options}
      onChange={handleChange}
      isSearchable
    />
  );
};

AbroadPollingStationField.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func,
  countries: PropTypes.arrayOf(PropTypes.string),
};

export default AbroadPollingStationField;
