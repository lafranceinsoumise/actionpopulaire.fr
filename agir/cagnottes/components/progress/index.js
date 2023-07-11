import React from "react";
import onDOMReady from "@agir/lib/utils/onDOMReady";

import "./style.scss";

import { renderReactComponent } from "@agir/lib/utils/react";
import SWRContext from "@agir/front/allPages/SWRContext";

import Progress from "./Progress";

const init = () => {
  const renderElement = document.getElementById("cagnottes_app");
  if (!renderElement) {
    return;
  }
  const dataElement = document.getElementById("cagnottes_data");
  const data =
    dataElement && dataElement.type === "application/json"
      ? JSON.parse(dataElement.textContent)
      : {};

  renderReactComponent(
    <SWRContext>
      <Progress {...data} />
    </SWRContext>,
    renderElement,
  );
};
onDOMReady(init);
