import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";

import SelectField from "@agir/front/formComponents/SelectField";

import DEPARTEMENTS from "@agir/front/formComponents/data/departements.json";

const DEPARTEMENT_OPTIONS = DEPARTEMENTS.map((d) => ({
  value: d.code,
  label: `${d.code} — ${d.nom}`,
}));

const DepartementField = (props) => {
  const { onChange, value, isMulti = false, ...rest } = props;

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

  const selectedValue = useMemo(() => {
    if (!value) {
      return value;
    }
    if (!isMulti) {
      return DEPARTEMENT_OPTIONS.find((d) => d.value === value);
    }
    const departements = Array.isArray(value) ? value : [value];
    return departements
      .map((departement) =>
        DEPARTEMENT_OPTIONS.find((d) => d.value === departement),
      )
      .filter(Boolean);
  }, [value, isMulti]);

  return (
    <SelectField
      {...rest}
      isSearchable
      isMulti={isMulti}
      value={selectedValue}
      options={DEPARTEMENT_OPTIONS}
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
};
export default DepartementField;
