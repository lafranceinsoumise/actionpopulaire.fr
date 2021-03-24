import onDOMReady from "@agir/lib/utils/onDOMReady";
import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: App },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./App"),
  ]);

  const init = () => {
    const renderElement = document.getElementById("mainApp");
    if (!renderElement) {
      return;
    }
    renderReactComponent(<App />, renderElement);
  };
  onDOMReady(init);
})();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    try {
      navigator.serviceWorker.register("/service-worker.js");
      log.debug("Registered service worker");
    } catch (e) {
      log.error("Failed to register service worker");
    }
  });
}
