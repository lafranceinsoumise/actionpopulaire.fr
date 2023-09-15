import PropTypes from "prop-types";
import React, { forwardRef, useCallback } from "react";
// eslint-disable-next-line no-unused-vars
import styled from "styled-components";

import TextField from "./TextField";

const NumberField = forwardRef((props, ref) => {
  const { value, onChange, currency = false, ...rest } = props;

  const handleChange = useCallback(
    (e) => {
      let numericValue =
        ("valueAsNumber" in e.target && e.target.numericValue) ||
        parseFloat(e.target.value);
      const stringValue = e.target.value;

      if (
        !numericValue ||
        isNaN(numericValue) ||
        stringValue.charAt(stringValue.length - 1) === "."
      ) {
        return onChange(stringValue);
      }

      if (numericValue && currency) {
        numericValue = numericValue * 100;
        numericValue = Math.abs(numericValue);
        numericValue = Math.floor(numericValue);
      }

      onChange(numericValue);
    },
    [onChange, currency],
  );

  const currentValue =
    typeof value !== "number" || isNaN(value) || !currency
      ? value || ""
      : value / 100;

  return (
    <TextField
      min="0"
      step="0.01"
      inputmode="decimal"
      type="number"
      lang="fr-FR"
      {...rest}
      ref={ref}
      onChange={handleChange}
      value={currentValue}
      textArea={false}
      css={`
        input {
          -moz-appearance: textfield;

          &::-webkit-outer-spin-button,
          &::-webkit-inner-spin-button {
            -webkit-appearance: none;
            margin: 0;
          }
        }
      `}
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
