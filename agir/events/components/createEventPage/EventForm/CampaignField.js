import PropTypes from "prop-types";
import React, { useCallback } from "react";

import RadioField from "@agir/front/formComponents/RadioField";

const NameField = (props) => {
  const { onChange, value, options, name, error, required, disabled } = props;

  const handleChange = useCallback(
    (value) => {
      onChange && onChange(name, value);
    },
    [name, onChange]
  );

  return (
    <RadioField
      label="Que cela concerne-t-il ?"
      id={name}
      name={name}
      value={value}
      onChange={handleChange}
      options={options}
      error={error}
      required={required}
      disabled={disabled}
    />
  );
};
NameField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string,
  options: PropTypes.arrayOf(PropTypes.object),
  name: PropTypes.string.isRequired,
  error: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default NameField;
