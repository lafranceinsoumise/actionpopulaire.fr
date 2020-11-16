import InputGroup from "@agir/lib/bootstrap/InputGroup";
import { parsePrice, displayNumber } from "@agir/lib/utils/display";
import PropTypes from "prop-types";
import React, { useState } from "react";

function valueToText(v) {
  if (v === null) {
    return "";
  } else if (v % 100 === 0) {
    return displayNumber(v / 100);
  } else {
    return displayNumber(v / 100, 2);
  }
}

const AmountInput = ({ placeholder, onChange, value, disabled }) => {
  const [text, setText] = useState("");

  if (value !== parsePrice(text)) {
    setText(valueToText(value));
  }

  return (
    <InputGroup className={value ? "selected" : ""}>
      <input
        type="text"
        className="form-control"
        placeholder={placeholder}
        step={1}
        disabled={disabled}
        onChange={(e) => {
          if (e.target.value === "") {
            setText("");
            if (value !== null) {
              onChange(null);
            }
          }
          const newValue = parsePrice(e.target.value);
          if (newValue !== null) {
            setText(e.target.value.replace(/\./, ","));
            if (newValue !== value) {
              onChange(newValue);
            }
          }
        }}
        value={text}
      />
      <InputGroup.Addon>€</InputGroup.Addon>
    </InputGroup>
  );
};

AmountInput.propTypes = {
  placeholder: PropTypes.string,
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
  value: PropTypes.number, // price in cents
};
AmountInput.defaultProps = {
  placeholder: "",
  onChange: () => null,
  disabled: false,
  value: null,
};

export default AmountInput;
