import ReactDOM from "react-dom";
import React from "react";
import { IBANField } from "./IBAN-field";
import onDOMReady from "@agir/lib/onDOMReady";

const renderIBANField = () => {
  const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

  if (iOS) {
    return;
  }

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
        allowedCountry={
          field.dataset.allowedCountries
            ? field.dataset.allowedCountries.split(",")
            : null
        }
        errorMessages={
          field.dataset.allowedCountriesError
            ? { wrongCountry: field.dataset.allowedCountriesError }
            : {}
        }
      />,
      renderingNode
    );
    parent.removeChild(field);
  }
};

onDOMReady(renderIBANField);
