import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";

import SelectField from "@agir/front/formComponents/SelectField";

import departements from "@agir/front/formComponents/data/departements.json";

const DEPARTEMENTS = departements.map((d) => ({
  value: d.code,
  label: `${d.code} — ${d.nom}`,
}));

const DepartementField = (props) => {
  const { onChange, value, ...rest } = props;

  const handleChange = useCallback(
    (departement) => {
      onChange && onChange(departement && departement.value);
    },
    [onChange],
  );

  const selectedValue = useMemo(
    () => value && DEPARTEMENTS.find((d) => d.value === value),
    [value],
  );

  return (
    <SelectField
      {...rest}
      isSearchable
      value={selectedValue}
      options={DEPARTEMENTS}
      onChange={handleChange}
    />
  );
};
DepartementField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.oneOf(["", ...DEPARTEMENTS.map((d) => d.value)]),
};
export default DepartementField;
