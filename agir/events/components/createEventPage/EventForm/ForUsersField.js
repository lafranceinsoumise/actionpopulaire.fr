import PropTypes from "prop-types";
import React, { useCallback, useEffect } from "react";

import RadioField from "@agir/front/formComponents/RadioField";

const ForUsersField = (props) => {
  const { onChange, value, options, name, error, required, disabled } = props;

  const handleChange = useCallback(
    (value) => {
      onChange && onChange(name, value);
    },
    [name, onChange]
  );

  useEffect(() => {
    Array.isArray(options) &&
      options.length === 1 &&
      handleChange(options[0].value);
  }, [options, handleChange]);

  return Array.isArray(options) && options.length > 1 ? (
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
  ) : null;
};
ForUsersField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string,
  options: PropTypes.arrayOf(PropTypes.object),
  name: PropTypes.string.isRequired,
  error: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default ForUsersField;
