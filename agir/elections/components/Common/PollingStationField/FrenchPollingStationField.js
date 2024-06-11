import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import useSWRImmutable from "swr/immutable";

import { getElectionEndpoint } from "@agir/elections/Common/api";

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

const FrenchPollingStationField = (props) => {
  const { value, name, onChange, commune, disabled } = props;

  const [selected, setSelected] = useState(null);

  const { data: pollingStations, isValidating: isLoading } = useSWRImmutable(
    commune && getElectionEndpoint("searchPollingStations", { commune }),
  );

  const handleChange = useCallback((pollingStation) => {
    setSelected(pollingStation);
  }, []);

  useEffect(() => {
    if (selected?.codeCommune !== commune) {
      setSelected(null);
      onChange({
        target: {
          name,
          value: "",
        },
      });
    }
  }, [name, commune, selected]);

  useEffect(() => {
    if (value === selected?.value) {
      return;
    }
    if (value && !selected?.value) {
      const s = Array.isArray(pollingStations)
        ? pollingStations.find((option) => option.value === value)
        : null;
      setSelected(s);
      return;
    }
    onChange({
      target: {
        name,
        value: selected?.value || "",
      },
    });
  }, [name, value, pollingStations, selected, onChange]);

  return (
    <SelectField
      placeholder="Sélectionner un bureau de vote"
      {...props}
      value={selected}
      options={pollingStations}
      onChange={handleChange}
      isSearchable
      disabled={disabled || isLoading || !commune}
    />
  );
};

FrenchPollingStationField.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func,
  countries: PropTypes.arrayOf(PropTypes.string),
  disabled: PropTypes.bool,
};

export default FrenchPollingStationField;
