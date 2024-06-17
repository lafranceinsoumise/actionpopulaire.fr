import PropTypes from "prop-types";
import React, { useEffect } from "react";
import { usePrevious } from "react-use";

import FrenchPollingStationField from "./FrenchPollingStationField";
import AbroadPollingStationField from "./AbroadPollingStationField";

const PollingStationField = ({ votingLocation, ...rest }) => {
  const { name, onChange } = rest;

  const isAbroad = votingLocation?.type === "consulate";
  const wasAbroad = usePrevious(isAbroad);

  useEffect(() => {
    if (typeof wasAbroad === "undefined" || wasAbroad === isAbroad) {
      return;
    }
    onChange({
      target: { name, value: "" },
    });
  }, [name, onChange, wasAbroad, isAbroad]);

  const placeholder = !votingLocation
    ? "Selectionnez d'abord une commune ou une ambassade"
    : "Sélectionnez un bureau de vote";

  return isAbroad ? (
    <AbroadPollingStationField
      label="Bureau de vote"
      {...rest}
      placeholder={placeholder}
      countries={votingLocation?.countries}
    />
  ) : (
    <FrenchPollingStationField
      label="Bureau de vote"
      {...rest}
      placeholder={placeholder}
      commune={votingLocation?.code}
    />
  );
};

PollingStationField.propTypes = {
  votingLocation: PropTypes.shape({
    code: PropTypes.string,
    type: PropTypes.oneOf(["commune", "consulate"]),
    countries: PropTypes.array,
  }),
  isAbroad: PropTypes.bool.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
};

export default PollingStationField;
