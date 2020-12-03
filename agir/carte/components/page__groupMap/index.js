import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { GlobalContextProvider },
    { default: GroupMap },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("@agir/front/genericComponents/GlobalContext"),
    import("./GroupMap.js"),
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
        <GroupMap />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(init);
})();
