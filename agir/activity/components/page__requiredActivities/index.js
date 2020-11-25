import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: RequiredActivityPage },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./RequiredActivityPage"),
    import("@agir/front/genericComponents/GlobalContext"),
  ]);

  const showActivities = () => {
    const dataElement = document.getElementById("exportedContent");
    const renderElement = document.getElementById("mainApp");
    if (!dataElement || !renderElement) {
      return;
    }
    const payload = JSON.parse(dataElement.textContent);
    renderReactComponent(
      <GlobalContextProvider>
        <RequiredActivityPage {...payload} />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(showActivities);
})();
