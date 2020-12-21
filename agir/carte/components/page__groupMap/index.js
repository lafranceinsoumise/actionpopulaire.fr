import onDOMReady from "@agir/lib/utils/onDOMReady";

import logger from "@agir/lib/utils/log";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { GlobalContextProvider },
    { default: GroupMap },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("@agir/front/globalContext/GlobalContext"),
    import("./GroupMap.js"),
  ]);

  const init = () => {
    const dataElement = document.getElementById("exportedContent");
    const renderElement = document.getElementById("mainApp");
    if (!dataElement || !renderElement) {
      return;
    }
    const payload = JSON.parse(dataElement.textContent);
    log.debug(payload);
    renderReactComponent(
      <GlobalContextProvider>
        <GroupMap {...payload} />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(init);
})();
