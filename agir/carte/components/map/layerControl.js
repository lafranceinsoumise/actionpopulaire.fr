import Control from "ol/control/Control";

import { element } from "./utils";
import fontawesome from "@agir/lib/utils/fontawesome";

export default function makeLayerControl(layersConfig, drawingFunction) {
  const selectors = layersConfig.map(function (layerConfig) {
    const input = element("input", [], { type: "checkbox", checked: true });
    const label = element("label", [
      input,
      ["span", [layerConfig.label], { style: { color: layerConfig.color } }],
    ]);

    input.addEventListener("change", function () {
      layerConfig.layer.setVisible(input.checked);
    });

    return label;
  });

  const layerButton = element("button", [fontawesome("bars")]);
  const layerButtonContainer = element("div", [layerButton], {
    className: "ol-unselectable ol-control layer_selector_button",
  });

  const layerBox = element("div", selectors, { className: "layer_selector" });

  layerButton.addEventListener("click", function () {
    layerButton.textContent = layerBox.classList.toggle("visible")
      ? fontawesome("times")
      : fontawesome("bars");
  });

  const activeCheckbox = element("input", [], {
    type: "checkbox",
    checked: true,
  });
  const activeCheckboxLabel = element("label", [
    activeCheckbox,
    " Groupes les plus actifs",
  ]);
  activeCheckbox.addEventListener("change", function () {
    drawingFunction(activeCheckbox.checked);
  });
  const layerActiveCheckboxContainer = element("div", [activeCheckboxLabel], {
    className: "ol-unselectable ol-control active_groups_button",
  });

  return [
    new Control({ element: layerActiveCheckboxContainer }),
    new Control({ element: layerButtonContainer }),
    new Control({ element: layerBox }),
  ];
}
