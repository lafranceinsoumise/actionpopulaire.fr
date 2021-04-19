import React, { Suspense } from "react";

import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";
import { lazy } from "@agir/front/app/utils";

(async function () {
  const PushModal = lazy(() => import("../allPages/PushModal"), <div />);
  const GlobalContextProvider = lazy(
    () => import("../globalContext/GlobalContext"),
    <div />
  );

  const showHeader = () => {
    renderReactComponent(
      <Suspense fallback={<div />}>
        <GlobalContextProvider>
          <PushModal isActive />
        </GlobalContextProvider>
      </Suspense>,
      document.getElementById("release-modal")
    );
  };
  onDOMReady(showHeader);
})();
