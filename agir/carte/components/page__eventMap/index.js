import onDOMReady from "@agir/lib/utils/onDOMReady";

const debug = require("debug")("agir:eventMap:init");

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { GlobalContextProvider },
    { default: EventMap },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("@agir/front/globalContext/GlobalContext"),
    import("./EventMap.js"),
  ]);

  const init = () => {
    const dataElement = document.getElementById("exportedContent");
    const renderElement = document.getElementById("mainApp");
    if (!dataElement || !renderElement) {
      return;
    }
    const payload = JSON.parse(dataElement.textContent);
    debug(payload);
    renderReactComponent(
      <GlobalContextProvider>
        <EventMap {...payload} />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(init);
})();
