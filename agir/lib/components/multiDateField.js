import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";
import React from "react";

import MultiDateInput from "@agir/front/formComponents/MultiDateField/MultiDateInput";
import ThemeProvider from "@agir/front/theme/ThemeProvider";

const renderField = (originalField) => {
  const parent = originalField.parentNode;
  const renderingNode = document.createElement("div");

  // const helpText = parent.querySelector("[id^='hint']")?.innerText;
  // const error = parent.querySelector("[id^='error']")?.innerText;

  renderReactComponent(
    <ThemeProvider>
      <MultiDateInput
        {...originalField.dataset}
        id={originalField.id}
        name={originalField.name}
        initialValue={originalField.value}
        minDate={originalField.min}
        maxDate={originalField.max}
        disabled={originalField.disabled}
        readOnly={originalField.readOnly}
      />
    </ThemeProvider>,
    renderingNode,
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
