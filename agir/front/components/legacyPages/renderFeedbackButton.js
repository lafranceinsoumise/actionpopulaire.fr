import React, { Suspense } from "react";

import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";
import { lazy } from "@agir/front/app/utils";

(async function () {
  const FeedbackButton = lazy(
    () => import("../allPages/FeedbackButton"),
    <div />
  );
  const GlobalContextProvider = lazy(
    () => import("../globalContext/GlobalContext"),
    <div />
  );

  const showHeader = () => {
    renderReactComponent(
      <Suspense fallback={<div />}>
        <GlobalContextProvider>
          <FeedbackButton />
        </GlobalContextProvider>
      </Suspense>,
      document.getElementById("feedback-button")
    );
  };
  onDOMReady(showHeader);
})();
