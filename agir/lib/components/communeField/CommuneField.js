import PropTypes from "prop-types";
import Async from "react-select/async";
import React from "react";
import search from "./search";
import { debounce } from "@agir/lib/utils/promises";

const types = {
  COM: "",
  ARM: "",
  COMA: ", commune associée",
  COMD: ", commune déléguée",
  SRM: ", secteur électoral",
};

const defaultSearch = debounce(search, 200);

const defaultValueGetter = ({ code, type }) => `${type}-${code}`;

const defaultLabelGetter = ({ nom, type, code_departement }) =>
  `${nom} (${code_departement}${types[type]})`;

const CommuneField = ({
  value,
  onChange,
  search,
  valueGetter,
  labelGetter,
  types,
}) => (
  <Async
    value={value}
    onChange={onChange}
    loadOptions={(q) =>
      search(q, types).then((results) =>
        results.map((c) => ({ value: valueGetter(c), label: labelGetter(c) })),
      )
    }
    cacheOptions
    loadingMessage={() => "Chargement des résultats..."}
    noOptionsMessage={({ inputValue }) =>
      inputValue.trim().length < 3
        ? "Cherchez une commune..."
        : "Pas de résultat"
    }
    placeholder="Cherchez votre commune"
  />
);
CommuneField.propTypes = {
  value: PropTypes.shape({ label: PropTypes.string, value: PropTypes.string }),
  onChange: PropTypes.func,
  search: PropTypes.func,
  valueGetter: PropTypes.func,
  labelGetter: PropTypes.func,
  types: PropTypes.arrayOf(PropTypes.string),
};
CommuneField.defaultProps = {
  value: null,
  onChange: () => null,
  search: defaultSearch,
  valueGetter: defaultValueGetter,
  labelGetter: defaultLabelGetter,
  types: [],
};

export default CommuneField;
