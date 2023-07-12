import React from "react";
import onDOMReady from "@agir/lib/utils/onDOMReady";
import App from "@agir/elus/parrainages/App";
import { renderReactComponent } from "@agir/lib/utils/react";
import { GlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import "@agir/front/genericComponents/style.scss";
import "./style.css";

const displayInterface = () => {
  const elusProchesScript = document.getElementById("elusProches");
  let elusProchesData = [];

  if (elusProchesScript && elusProchesScript.type === "application/json") {
    elusProchesData = JSON.parse(elusProchesScript.textContent);
  }

  renderReactComponent(
    <GlobalContextProvider>
      <App elusProches={elusProchesData} />
    </GlobalContextProvider>,
    document.getElementById("app"),
  );

  const appLoader = document.getElementById("app_loader");
  if (appLoader) {
    appLoader.remove();
  }
};
onDOMReady(displayInterface);
export { Error } from "@agir/elus/parrainages/utils";
export { MarginBlock } from "@agir/elus/parrainages/utils";
