import React from "react";
import { renderReactComponent } from "@agir/lib/utils/react";
import MultiDateInput from "@agir/front/formComponents/MultiDateField/MultiDateInput";
import onDOMReady from "@agir/lib/utils/onDOMReady";

const renderField = (originalField) => {
  const parent = originalField.parentNode;
  const renderingNode = document.createElement("div");

  // const helpText = parent.querySelector("[id^='hint']")?.innerText;
  // const error = parent.querySelector("[id^='error']")?.innerText;

  renderReactComponent(
    <MultiDateInput
      {...originalField.dataset}
      id={originalField.id}
      name={originalField.name}
      initialValue={originalField.value}
      minDate={originalField.min}
      maxDate={originalField.max}
    />,
    renderingNode
  );

  parent.classList.remove("progress");
  parent.removeChild(originalField);
  parent.appendChild(renderingNode, parent);
};

onDOMReady(() => {
  document
    .querySelectorAll('input[data-component="MultiDateInput"]')
    .forEach(renderField);
});
