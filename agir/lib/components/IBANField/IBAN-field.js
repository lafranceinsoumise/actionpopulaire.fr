import React, { useEffect, useRef, useState } from "react";

import PropTypes from "prop-types";
import {
  isIBANValid,
  formatInputContent,
} from "@agir/lib/IBANField/validation";

const errorMessages = {
  wrongCountry: "La nationalité de cet IBAN n'est pas acceptée.",
  invalid: "Cet IBAN est invalide.",
};

function HelpBlock({ children }) {
  return children && <span className="help-block">{children}</span>;
}

function checkIfError(value, allowedCountries) {
  if (value === "") {
    return null;
  } else if (
    allowedCountries !== null &&
    !allowedCountries.includes(value.slice(0, 2))
  ) {
    return errorMessages.wrongCountry;
  } else if (!isIBANValid(value)) {
    return errorMessages.invalid;
  }
  return null;
}

const IBANField = ({ id, name, initial, placeholder, allowedCountries }) => {
  const [inputState, setInputState] = useState({ value: initial, cursor: 0 });
  const [error, setError] = useState(null);
  const ref = useRef();

  useEffect(() => {
    if (ref.current) {
      ref.current.setSelectionRange(inputState.cursor, inputState.cursor);
    }
  }, [inputState]);

  return (
    <div className={error && "has-error"}>
      <input
        ref={ref}
        id={id}
        name={name}
        type="text"
        className={"form-control"}
        placeholder={placeholder}
        value={inputState.value}
        onChange={(e) => {
          setInputState(
            formatInputContent(
              ref.current.value,
              ref.current.selectionStart,
              e.nativeEvent.inputType === "deleteContentBackward",
            ),
          );
        }}
        onBlur={() =>
          setError(checkIfError(inputState.value, allowedCountries))
        }
        onFocus={() => setError(null)}
      />
      {error && <HelpBlock>{error}</HelpBlock>}
    </div>
  );
};

IBANField.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  initial: PropTypes.string,
  placeholder: PropTypes.string,
  allowedCountries: PropTypes.arrayOf(PropTypes.string),
};

IBANField.defaultProps = {
  initial: "",
  placeholder: "IBAN",
  allowedCountries: null,
};

HelpBlock.propTypes = {
  children: PropTypes.oneOfType([PropTypes.element, PropTypes.string]),
};

export default IBANField;
