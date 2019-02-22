import ReactDOM from "react-dom";
import React from "react";
import { IBANField } from "./IBAN-field";
import onDOMReady from "@agir/lib/onDOMReady";

const renderIBANField = () => {
  const fields = document.querySelectorAll('input[data-component="IBANField"]');

  for (let field of fields) {
    const renderingNode = document.createElement("div");
    const parent = field.parentNode;
    parent.appendChild(renderingNode);
    ReactDOM.render(
      <IBANField
        name={field.name}
        id={field.id}
        placeholder={"Entrez votre Iban"}
        allowedCountry={["FR"]}
      />,
      renderingNode
    );
    parent.removeChild(field);
  }
};

onDOMReady(renderIBANField);
