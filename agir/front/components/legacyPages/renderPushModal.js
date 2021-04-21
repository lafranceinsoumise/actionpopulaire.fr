import React from "react";

import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";

import GlobalContextProvider from "@agir/front/globalContext/GlobalContext";
import PushModal from "@agir/front/allPages/PushModal";

const showHeader = () => {
  renderReactComponent(
    <GlobalContextProvider>
      <PushModal isActive />
    </GlobalContextProvider>,
    document.getElementById("release-modal")
  );
};
onDOMReady(showHeader);
