import onDOMReady from "@agir/lib/utils/onDOMReady";

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
