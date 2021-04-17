import React, { Suspense } from "react";

import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";
import { lazy } from "@agir/front/app/utils";

(async function () {
  const TopBar = lazy(() => import("../allPages/TopBar"), <div />);
  const GlobalContextProvider = lazy(
    () => import("../globalContext/GlobalContext"),
    <div />
  );

  const showHeader = () => {
    renderReactComponent(
      <Suspense fallback={<div />}>
        <GlobalContextProvider>
          <TopBar />
        </GlobalContextProvider>
      </Suspense>,
      document.getElementById("top-bar")
    );
  };
  onDOMReady(showHeader);
})();
