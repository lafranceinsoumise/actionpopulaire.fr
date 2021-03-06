import React from "react";

import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";

import GlobalContextProvider from "@agir/front/globalContext/GlobalContext";
import TopBar from "@agir/front/allPages/TopBar";

const showHeader = () => {
  renderReactComponent(
    <GlobalContextProvider>
      <TopBar />
    </GlobalContextProvider>,
    document.getElementById("top-bar")
  );
};

onDOMReady(showHeader);
