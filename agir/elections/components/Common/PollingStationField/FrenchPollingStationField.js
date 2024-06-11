import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import useSWRImmutable from "swr/immutable";

import { getElectionEndpoint } from "@agir/elections/Common/api";

import Spacer from "@agir/front/genericComponents/Spacer";
import SelectField from "@agir/front/formComponents/SelectField";
import TextField from "@agir/front/formComponents/TextField";

const UNKNOWN_POLLING_STATION_OPTION = {
  id: "unknown",
  label: "Mon bureau n'est pas dans la liste",
  value: "",
};

const FrenchPollingStationField = (props) => {
  const {
    value,
    name,
    onChange,
    onChangeCirconscriptionLegislative,
    commune,
    disabled,
  } = props;

  const [selected, setSelected] = useState(null);

  const { data: pollingStations, isValidating: isLoading } = useSWRImmutable(
    commune && getElectionEndpoint("searchPollingStations", { commune }),
  );

  const options = useMemo(
    () =>
      Array.isArray(pollingStations)
        ? [...pollingStations, { ...UNKNOWN_POLLING_STATION_OPTION, commune }]
        : [{ ...UNKNOWN_POLLING_STATION_OPTION, commune }],
    [pollingStations, commune],
  );

  const handleChange = useCallback(
    (value = "") => {
      onChange({
        target: {
          name,
          value: typeof value === "object" ? value.target.value : value,
        },
      });
    },
    [onChange, name],
  );

  const handleSelect = useCallback(
    (pollingStation) => {
      setSelected(pollingStation);

      if (pollingStation.id === UNKNOWN_POLLING_STATION_OPTION.id) {
        handleChange();
      }
    },
    [handleChange],
  );

  useEffect(() => {
    if (
      selected &&
      selected.id !== UNKNOWN_POLLING_STATION_OPTION.id &&
      selected.codeCommune !== commune
    ) {
      setSelected(null);
      handleChange();
    }
  }, [handleChange, commune, selected]);

  useEffect(() => {
    if (isLoading || value === selected?.value) {
      return;
    }

    if (selected?.id === UNKNOWN_POLLING_STATION_OPTION.id) {
      return;
    }

    if (value && !selected) {
      const matchingValue =
        (Array.isArray(pollingStations) &&
          pollingStations.find((option) => option.value === value)) ||
        UNKNOWN_POLLING_STATION_OPTION;

      setSelected(matchingValue);
      return;
    }

    handleChange(selected?.value);
  }, [name, value, pollingStations, selected, onChange, isLoading]);

  useEffect(() => {
    onChangeCirconscriptionLegislative &&
      selected?.circonscription &&
      onChangeCirconscriptionLegislative(selected.circonscription);
  }, [onChangeCirconscriptionLegislative, selected?.circonscription]);

  return (
    <>
      <SelectField
        placeholder="Sélectionner un bureau de vote"
        {...props}
        value={selected}
        options={options}
        onChange={handleSelect}
        isSearchable
        disabled={disabled || isLoading || !commune}
      />
      {selected?.id === UNKNOWN_POLLING_STATION_OPTION.id && (
        <>
          <Spacer size="1rem" />
          <TextField
            small
            label="Bureau de vote"
            placeholder={`Exemple : ${options[0]?.label || ""}`}
            value={value}
            onChange={handleChange}
          />
        </>
      )}
    </>
  );
};

FrenchPollingStationField.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func,
  onChangeCirconscriptionLegislative: PropTypes.func,
  countries: PropTypes.arrayOf(PropTypes.string),
  disabled: PropTypes.bool,
};

export default FrenchPollingStationField;
