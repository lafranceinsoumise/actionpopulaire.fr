import PropTypes from "prop-types";
import React, { useEffect, useMemo } from "react";

import SelectField from "@agir/front/formComponents/SelectField";

import { getCirconscriptionLegislativeSearchLink } from "@agir/elections/Common/utils";

const CirconscriptionLegislativeField = (props) => {
  const {
    value = null,
    onChange,
    disabled,
    options = [],
    votingLocation,
    ...rest
  } = props;

  const departement = votingLocation ? votingLocation.departement : undefined;
  const byDepartement = useMemo(() => {
    if (!Array.isArray(options) || options.length === 0) {
      return [];
    }
    let result = options;
    if (typeof departement !== "undefined") {
      result = options.filter((option) => option.departement === departement);
    }

    return result.map((option) => ({ ...option, value: option.code }));
  }, [options, departement]);

  useEffect(() => {
    if (
      typeof value === "string" &&
      Array.isArray(options) &&
      options.length > 0
    ) {
      onChange(options.find((option) => option.code === value) || null);
    }
  }, [onChange, options, value]);

  return (
    <SelectField
      helpText={
        <span>
          Vous pouvez vérifier votre circonscription d'inscription sur le site{" "}
          <a
            href={getCirconscriptionLegislativeSearchLink(votingLocation)}
            target="_blank"
            rel="noopener noreferrer"
          >
            nosdeputes.fr
          </a>
        </span>
      }
      placeholder="Chercher un circonscription"
      {...rest}
      value={typeof value === "string" ? null : value}
      options={byDepartement}
      onChange={onChange}
      disabled={
        disabled ||
        byDepartement.length === 0 ||
        typeof departement === "undefined"
      }
    />
  );
};

CirconscriptionLegislativeField.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  onChange: PropTypes.func,
  options: PropTypes.arrayOf(PropTypes.object),
};

export default CirconscriptionLegislativeField;
