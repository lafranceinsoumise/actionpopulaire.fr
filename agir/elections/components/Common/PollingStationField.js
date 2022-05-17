import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import { usePrevious } from "react-use";

import SearchAndSelectField from "@agir/front/formComponents/SearchAndSelectField";
import TextField from "@agir/front/formComponents/TextField";

import ABROAD_POLLING_STATIONS from "./abroadPollingStations";

const ABROAD_POLLING_STATION_OPTIONS = ABROAD_POLLING_STATIONS.map(
  ({ country, list, pollingStation }) => {
    const value = `${pollingStation} / ${list} (${country})`;
    return {
      label: value,
      value: value,
      normalizedValue: value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase(),
    };
  }
);

const HelpText = (
  <span>
    Vous pouvez vérifier votre bureau de vote sur votre carte éléctorale ou sur{" "}
    <a
      href="https://www.service-public.fr/particuliers/vosdroits/services-en-ligne-et-formulaires/ISE"
      target="_blank"
      rel="noopener noreferrer"
    >
      le site du service public
    </a>
  </span>
);

const AbroadPollingStationField = (props) => {
  const { value, name, onChange } = props;

  const [selected, setSelected] = useState(
    ABROAD_POLLING_STATION_OPTIONS.find((option) => option.value === value)
  );
  const [options, setOptions] = useState(ABROAD_POLLING_STATION_OPTIONS);

  const handleChange = useCallback((pollingStation) => {
    setSelected(pollingStation);
  }, []);

  const handleSearch = useCallback(
    async (searchTerm) =>
      await new Promise((resolve) => {
        if (!searchTerm) {
          setOptions(ABROAD_POLLING_STATION_OPTIONS);
          resolve(ABROAD_POLLING_STATION_OPTIONS);
          return;
        }
        searchTerm = searchTerm
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "")
          .toLowerCase();
        const filteredContries = ABROAD_POLLING_STATION_OPTIONS.filter(
          (option) => option.normalizedValue.includes(searchTerm)
        );
        setOptions(filteredContries);
        resolve(filteredContries);
      }),
    []
  );

  useEffect(() => {
    onChange({
      target: {
        name,
        value: selected?.value || "",
      },
    });
  }, [name, onChange, selected]);

  return (
    <SearchAndSelectField
      {...props}
      placeholder="Chercher un bureau de vote"
      value={selected}
      minSearchTermLength={0}
      defaultOptions={options}
      onChange={handleChange}
      onSearch={handleSearch}
    />
  );
};

AbroadPollingStationField.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func,
};

const PollingStationField = ({ isAbroad, ...rest }) => {
  const { name, onChange } = rest;
  const wasAbroad = usePrevious(isAbroad);
  useEffect(() => {
    if (typeof wasAbroad === "undefined" || wasAbroad === isAbroad) {
      return;
    }
    onChange({
      target: { name, value: "" },
    });
  }, [name, onChange, wasAbroad, isAbroad]);

  return isAbroad ? (
    <AbroadPollingStationField
      helpText={HelpText}
      label="Bureau de vote"
      {...rest}
    />
  ) : (
    <TextField helpText={HelpText} label="Bureau de vote" {...rest} />
  );
};

PollingStationField.propTypes = {
  isAbroad: PropTypes.bool.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
};
export default PollingStationField;
