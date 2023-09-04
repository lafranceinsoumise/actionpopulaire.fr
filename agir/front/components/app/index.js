import "core-js/es/string/replace-all";

import React from "react";
import onDOMReady from "@agir/lib/utils/onDOMReady";
import logger from "@agir/lib/utils/logger";

import "@agir/front/allPages/sentry";
import "@agir/front/allPages/ios";
import "@agir/front/allPages/fonts/fonts.css";
import "@agir/front/genericComponents/style.scss";

import { renderReactComponent } from "@agir/lib/utils/react";

import App from "@agir/front/app/App";

const log = logger(__filename);

const init = () => {
  const renderElement = document.getElementById("mainApp");
  if (!renderElement) {
    return;
  }
  renderReactComponent(<App />, renderElement);
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
