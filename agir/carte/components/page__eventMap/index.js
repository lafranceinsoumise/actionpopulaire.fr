import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { GlobalContextProvider },
    { default: EventMap },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("@agir/front/genericComponents/GlobalContext"),
    import("./EventMap.js"),
  ]);

  const init = () => {
    const dataElement = document.getElementById("exportedContent");
    const renderElement = document.getElementById("mainApp");
    if (!dataElement || !renderElement) {
      return;
    }
    const payload = JSON.parse(dataElement.textContent);
    console.log(payload);
    renderReactComponent(
      <GlobalContextProvider>
        <EventMap />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(init);
})();
