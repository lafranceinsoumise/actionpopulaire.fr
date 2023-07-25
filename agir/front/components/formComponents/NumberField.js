import PropTypes from "prop-types";
import React, { forwardRef, useCallback } from "react";
// eslint-disable-next-line no-unused-vars
import styled from "styled-components";

import TextField from "./TextField";

const NumberField = forwardRef((props, ref) => {
  const { value, onChange, currency = false } = props;

  const handleChange = useCallback(
    (e) => {
      let newAmount = parseFloat(e.target.value || 0);

      if (isNaN(newAmount)) {
        newAmount = 0;
      }

      if (newAmount && currency) {
        newAmount = newAmount * 100;
        newAmount = Math.abs(newAmount);
        newAmount = Math.floor(newAmount);
      }

      onChange(newAmount);
    },
    [onChange, currency]
  );

  const currentValue = currency && value ? value / 100 : value ? value : "";

  return (
    <TextField
      min="0"
      step="1"
      {...props}
      type="number"
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
  onChange: PropTypes.func.isRequired,
  currency: PropTypes.bool,
};

NumberField.displayName = "NumberField";

export default NumberField;
