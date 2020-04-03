import PropTypes from "prop-types";
import Async from "react-select/async/dist/react-select.esm";
import React, { useState } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import onDOMReady from "@agir/lib/onDOMReady"; // doit être importé avant React

const url = "/chercher-commune/";

const types = {
  COM: "",
  ARM: "",
  COMA: ", commune associée",
  COMD: ", commune déléguée"
};

const format = ({ code, nom, type }) => {
  return {
    value: `${type}-${code}`,
    label: `${nom} (${code.slice(0, 2)}${types[type]})`
  };
};

const query = q =>
  axios
    .get(url, {
      params: { q },
      headers: { Accept: "application/json" }
    })
    .then(
      res => res.data.results.map(format),
      () => {
        throw new Error("Problème de connexion.");
      }
    );

const Select = ({ value, onChange }) => (
  <Async
    value={value}
    onChange={onChange}
    loadOptions={query}
    cacheOptions
    loadingMessage={() => "Chargement des résultats..."}
    noOptionsMessage={() => "Pas de résultat"}
    placeholder="Cherchez votre commune"
  />
);
Select.propTypes = {
  value: PropTypes.shape({ label: PropTypes.string, value: PropTypes.string }),
  onChange: PropTypes.func
};

const RootComponent = ({ name, initial }) => {
  const [value, setValue] = useState(initial);

  return (
    <>
      <input type="hidden" name={name} value={value ? value.value : ""} />
      <Select value={value} onChange={setValue} />
    </>
  );
};
RootComponent.propTypes = {
  name: PropTypes.string,
  initial: PropTypes.shape({ label: PropTypes.string, value: PropTypes.string })
};

function render() {
  const communeFields = document.querySelectorAll('input[data-commune="Y"]');

  for (let field of communeFields) {
    const insertingNode = field.parentNode;
    const props = { initial: null, name: field.name };
    if (field.value) {
      props.initial = { value: field.value, label: field.dataset.label };
    }
    insertingNode.removeChild(field);
    ReactDOM.render(<RootComponent {...props} />, insertingNode);
  }
}

onDOMReady(render);
