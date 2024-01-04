import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";

import SelectField from "@agir/front/formComponents/SelectField";

import DEPARTEMENTS from "@agir/front/formComponents/data/departements.json";
import CIRCONSCRIPTIONS_FE from "@agir/front/formComponents/data/circonscriptionsFE.json";

const DEPARTEMENT_OPTIONS = DEPARTEMENTS.map((d) => ({
  value: d.code,
  label: `${d.code} — ${d.nom}`,
}));

const CIRCONSCRIPTION_FE_OPTIONS = CIRCONSCRIPTIONS_FE.map((c) => ({
  value: c.code,
  label: `${c.code} — ${c.nom}`,
}));

const DepartementField = (props) => {
  const {
    onChange,
    value,
    isMulti = false,
    withCirconscriptionFE = false,
    ...rest
  } = props;

  const handleChange = useCallback(
    (selected) => {
      const value =
        isMulti && Array.isArray(selected)
          ? selected.map((departement) => departement.value)
          : selected?.value;

      onChange && onChange(value);
    },
    [onChange, isMulti],
  );

  const options = useMemo(() => {
    if (!withCirconscriptionFE) {
      return DEPARTEMENT_OPTIONS;
    }

    return [...DEPARTEMENT_OPTIONS, ...CIRCONSCRIPTION_FE_OPTIONS];
  }, [withCirconscriptionFE]);

  const selectedValue = useMemo(() => {
    if (!value) {
      return value;
    }
    if (!isMulti) {
      return options.find((d) => d.value === value);
    }
    const departements = Array.isArray(value) ? value : [value];
    return departements
      .map((departement) => options.find((d) => d.value === departement))
      .filter(Boolean);
  }, [options, value, isMulti]);

  return (
    <SelectField
      {...rest}
      isSearchable
      isMulti={isMulti}
      value={selectedValue}
      options={options}
      onChange={handleChange}
    />
  );
};
DepartementField.propTypes = {
  onChange: PropTypes.func,
  value: PropTypes.oneOfType([
    PropTypes.oneOf(["", ...DEPARTEMENT_OPTIONS.map((d) => d.value)]),
    PropTypes.arrayOf(
      PropTypes.oneOf(["", ...DEPARTEMENT_OPTIONS.map((d) => d.value)]),
    ),
  ]),
  isMulti: PropTypes.bool,
  withCirconscriptionFE: PropTypes.bool,
};
export default DepartementField;
