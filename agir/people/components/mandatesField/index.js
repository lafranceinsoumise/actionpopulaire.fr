import "core-js/stable";
import "regenerator-runtime/runtime";

import React from "react";
import ReactDOM from "react-dom";

import MandatesField from "./mandatesField";
import onDOMReady from "@agir/lib/onDOMReady";

const renderMandatesFields = function () {
  const hiddenFields = document.querySelectorAll('input[data-mandates="Y"]');

  for (let hiddenField of hiddenFields) {
    if (!hiddenField.dataset.mandatesRendered) {
      const renderingNode = document.createElement("div");
      hiddenField.type = "hidden";
      hiddenField.parentNode.appendChild(renderingNode);
      ReactDOM.render(
        <MandatesField hiddenField={hiddenField} />,
        renderingNode
      );
      hiddenField.dataset.mandatesRendered = true;
    }
  }
};

onDOMReady(renderMandatesFields);
