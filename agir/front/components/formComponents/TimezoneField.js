import PropTypes from "prop-types";
import React, { useCallback } from "react";

import SelectField from "@agir/front/formComponents/SelectField";

import TIMEZONES from "./timezones";

const timezones = TIMEZONES.map((tz) => ({
  value: tz,
  label: tz,
}));

const TimezoneField = (props) => {
  const { onChange, value, ...rest } = props;

  const handleChange = useCallback(
    (timezone) => {
      onChange && onChange(timezone?.value);
    },
    [onChange],
  );

  let currentValue = value && timezones.find((tz) => tz.value === value);
  if (!value) {
    // Default to client timezone if props.value is falsy
    currentValue = timezones.find(
      (tz) => tz.value === Intl.DateTimeFormat().resolvedOptions().timeZone,
    );
  }

  return (
    <SelectField
      {...rest}
      isSearchable
      value={currentValue}
      options={timezones}
      onChange={handleChange}
    />
  );
};
TimezoneField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.oneOf(["", ...TIMEZONES]),
};
export default TimezoneField;
