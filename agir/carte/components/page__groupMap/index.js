import onDOMReady from "@agir/lib/utils/onDOMReady";

import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

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

    renderReactComponent(
      <GlobalContextProvider hasToasts>
        <GroupMap {...payload} />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(init);
})();
