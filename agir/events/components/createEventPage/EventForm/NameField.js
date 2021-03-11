import PropTypes from "prop-types";
import React, { useCallback } from "react";

import TextField from "@agir/front/formComponents/TextField";

const NameField = (props) => {
  const { onChange, value, name, error, required, disabled } = props;

  const handleChange = useCallback(
    (e) => {
      onChange && onChange(name, e.target.value);
    },
    [name, onChange]
  );

  return (
    <TextField
      label="Nom de l'événement"
      id={name}
      name={name}
      value={value}
      onChange={handleChange}
      error={error}
      required={required}
      disabled={disabled}
      maxLength={100}
      hasCounter={!!value && value.length >= 50}
    />
  );
};
NameField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string,
  name: PropTypes.string.isRequired,
  error: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default NameField;
