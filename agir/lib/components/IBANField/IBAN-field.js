import React from "react";

import PropTypes from "prop-types";

/**
 * Converti un les lettres d'un IBAN en une chaine de caractère de 2 chiffre selon la convention de calcul des IBAN:
 *  A:"10", B:"11", C:"12" ... (Les chiffres ne sont pas affectés).
 * @param {string} iban - L'IBAN à traiter
 * @returns {string} - L'IBAN avec les lettres remplacées.
 */
function convertIBANLetters(iban) {
  let replacedIBAN = "";

  for (let i = 0; i < iban.length; i++) {
    const c = iban[i];

    if ((c >= "A" && c <= "Z") || (c >= "0" && c <= "9"))
      replacedIBAN += String(parseInt(c, 36));
  }
  return replacedIBAN;
}

/**
 * Insert des espace tout les 4 charactère
 * @param {string} rawValue
 * @param {number} rawCursor
 * @returns {{outValue: string, outCursor: number}}
 */
function insertSeparator(rawValue, rawCursor) {
  let formatedBeforCursor = "",
    formatedAfterCursor = "",
    i;

  for (i = 0; i < rawCursor; i += 4) {
    formatedBeforCursor += rawValue.slice(i, Math.min(i + 4, rawCursor));
    if (i + 4 < rawCursor) formatedBeforCursor += " ";
  }
  const rest =
    rawValue.slice(rawCursor, i) +
    (rawCursor < rawValue.length && rawCursor ? " " : "");
  for (; i < rawValue.length; i += 4) {
    formatedAfterCursor += rawValue.slice(i, i + 4);
    if (i + 4 < rawValue.length) formatedAfterCursor += " ";
  }
  return {
    outValue: formatedBeforCursor + rest + formatedAfterCursor,
    outCursor: formatedBeforCursor.length
  };
}

/**
 * Applique l'operation modulo sur un nombre contenue dans un tableau.
 * @param {Array.<number>} arrNbr - Un tableau contenant les différentes partie du nombre.
 * L'index 0 représente la plus petite partie (Little endian style)
 * @param {number} tenPower - Le nombre de chiffre par case du tableau
 * @param {number} mod - the
 * @returns {number}
 */
export function arrayNumberModulo(arrNbr, tenPower, mod) {
  let rest = 0;
  const base = Math.pow(10, tenPower);

  for (let i = arrNbr.length - 1; i >= 0; i--) {
    rest = (base * rest + arrNbr[i]) % mod;
  }
  return rest;
}

/**
 *  Convertie une chaîne de caractère en un tableau contenant les différentes partie du nombre.
 * L'index 0 représente la plus petite partie (Little endian style)
 * @param {String} strNbr - Une chaîne de caractère qui décrit le nombre
 * @param {number} tenPower - Le nombre de digit par case du tableau.
 * @returns {Array.<number>} - Le tableau décrivant le nombre.
 */
export function strToArrayNumber(strNbr, tenPower) {
  let arrayNbr = [];
  const max = Math.ceil(strNbr.length / tenPower);

  for (let i = 0, id_char = strNbr.length; i < max; i++, id_char -= tenPower) {
    const first = Math.max(id_char - tenPower, 0);
    arrayNbr[i] = first !== id_char ? strNbr.slice(first, id_char) : "0";
    arrayNbr[i] = parseInt(arrayNbr[i]);
  }
  return arrayNbr;
}

function getRawValue(input, cursor) {
  const str = input.toUpperCase();
  const partBeforeCursor = str.slice(0, cursor).replace(/[^A-Z0-9]/g, "");
  const partAfterCursor = str.slice(cursor).replace(/[^A-Z0-9]/g, "");

  return {
    rawValue: partBeforeCursor + partAfterCursor,
    rawCursor: partBeforeCursor.length
  };
}

export function isIbanValid(iban) {
  const tenPower = 8;
  const { rawValue } = getRawValue(iban, 0);
  const value = rawValue.slice(4, rawValue.length) + rawValue.slice(0, 4);
  const ibanTab = strToArrayNumber(convertIBANLetters(value), tenPower);
  const remainder = arrayNumberModulo(ibanTab, tenPower, 97);
  return remainder === 1;
}

function HelpBlock({ children }) {
  return children && <span className="help-block">{children}</span>;
}

export class IBANField extends React.Component {
  constructor(props, context) {
    super(props, context);

    const allowedContry = this.props.allowedCountry
      ? this.props.allowedCountry
      : [];

    this.state = {
      allowedCountry: allowedContry,
      error: null,
      value: "",
      cursorPosition: 0
    };
  }

  get errorMessages() {
    return { ...IBANField.defaultErrorMessages, ...this.props.errorMessages };
  }

  clearError() {
    this.setState({
      error: null
    });
  }

  checkError() {
    if (this.state.value === "") {
      this.clearError();
    } else if (
      !this.state.allowedCountry.includes(this.state.value.slice(0, 2))
    ) {
      this.setState({ error: this.errorMessages.wrongCountry });
    } else if (!isIbanValid(this.state.value)) {
      this.setState({ error: this.errorMessages.invalid });
    } else {
      this.clearError();
    }
  }

  handleBlur() {
    this.checkError();
  }

  handleFocus() {
    this.clearError();
  }

  handleChange(event) {
    const inValue = event.target.value;
    const inCursor = event.target.selectionStart;
    const { rawValue, rawCursor } = getRawValue(inValue, inCursor);
    const { outValue, outCursor } = insertSeparator(rawValue, rawCursor);

    this.setState({
      value: outValue,
      cursorPosition: outCursor
    });
  }

  render() {
    return (
      <div className={this.state.error === null ? "" : "has-error"}>
        <input
          ref={node => {
            if (node && node === document.activeElement) {
              const pos = this.state.cursorPosition;
              if (pos !== undefined) {
                node.selectionStart = node.selectionEnd = pos;
              }
            }
          }}
          id={this.props.id}
          name={this.props.name}
          type="text"
          className={"form-control"}
          placeholder={this.props.placeholder}
          value={this.state.value}
          onChange={this.handleChange.bind(this)}
          onBlur={this.handleBlur.bind(this)}
          onFocus={this.handleFocus.bind(this)}
        />
        <HelpBlock>{this.state.error}</HelpBlock>
      </div>
    );
  }
}

IBANField.defaultErrorMessages = {
  wrongCountry: "La nationalité de cet IBAN n'est pas acceptée.",
  invalid: "Cet IBAN est invalide."
};

IBANField.propTypes = {
  errorMessages: PropTypes.objectOf(PropTypes.string),
  allowedCountry: PropTypes.arrayOf(PropTypes.string),
  id: PropTypes.string,
  placeholder: PropTypes.string,
  name: PropTypes.string
};

HelpBlock.propTypes = {
  children: PropTypes.element
};

// export default IBANField;
