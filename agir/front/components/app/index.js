import React, { Suspense } from "react";
import onDOMReady from "@agir/lib/utils/onDOMReady";
import logger from "@agir/lib/utils/logger";

import "@agir/front/allPages/sentry";
import "@agir/front/allPages/ios.js";
import "@agir/front/genericComponents/style.scss";
import { renderReactComponent } from "@agir/lib/utils/react";
import { lazy } from "@agir/front/app/utils";

const log = logger(__filename);

const App = lazy(() => import("@agir/front/app/App"), null);

const init = () => {
  const renderElement = document.getElementById("mainApp");
  if (!renderElement) {
    return;
  }
  renderReactComponent(
    <Suspense fallback={null}>
      <App />
    </Suspense>,
    renderElement
  );
};
onDOMReady(init);

if ("serviceWorker" in navigator) {
  window.addEventListener("load", async () => {
    try {
      window.AgirSW = await navigator.serviceWorker.register("/sw.js");
      log.debug("Registered service worker");
    } catch (e) {
      log.error("Failed to register service worker");
    }
  });

  window.addEventListener("beforeinstallprompt", (e) => {
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
  });
}
