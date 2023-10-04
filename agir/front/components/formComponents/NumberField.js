import PropTypes from "prop-types";
import React, { forwardRef, useCallback, useState } from "react";

import TextField from "./TextField";

const NumberField = forwardRef((props, ref) => {
  const { value, onChange, currency = false, ...rest } = props;

  const [currentValue, setCurrentValue] = useState(
    String(
      typeof value !== "number" || isNaN(value) || !currency
        ? value || ""
        : (value / 100).toFixed(2),
    ).replace(".", ","),
  );

  const handleChange = useCallback(
    (e) => {
      const stringValue = e.target.value.trim().replace(/[^0-9,.]/g, "");

      setCurrentValue(stringValue);

      let numericValue =
        e.target?.numericValue || parseFloat(stringValue.replace(",", "."));

      if (!numericValue || isNaN(numericValue)) {
        return onChange(stringValue);
      }

      if (numericValue && currency) {
        numericValue = numericValue * 100;
        numericValue = Math.abs(numericValue);
        numericValue = Math.floor(numericValue);
      }

      onChange(numericValue);
    },
    [currency, onChange],
  );

  return (
    <TextField
      min="0"
      step="0.01"
      inputMode="decimal"
      lang="fr-FR"
      {...rest}
      ref={ref}
      onChange={handleChange}
      value={currentValue}
      textArea={false}
      icon={currency ? "euro-sign" : undefined}
    />
  );
});

NumberField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func,
  currency: PropTypes.bool,
};

NumberField.displayName = "NumberField";

export default NumberField;
