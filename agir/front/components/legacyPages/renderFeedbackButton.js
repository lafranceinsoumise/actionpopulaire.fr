import React from "react";

import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";

import GlobalContextProvider from "@agir/front/globalContext/GlobalContext";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";

const showHeader = () => {
  renderReactComponent(
    <GlobalContextProvider>
      <FeedbackButton />
    </GlobalContextProvider>,
    document.getElementById("feedback-button")
  );
};
onDOMReady(showHeader);
