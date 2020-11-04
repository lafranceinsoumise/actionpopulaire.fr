import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: ActivityList },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./ActivityList"),
    import("@agir/front/genericComponents/GobalContext"),
  ]);

  const showActivities = () => {
    const dataElement = document.getElementById("exportedContent");
    const renderElement = document.getElementById("mainApp");

    if (!dataElement || !renderElement) {
      return;
    }

    const payload = JSON.parse(dataElement.textContent);
    console.log(payload);
    renderReactComponent(
      <GlobalContextProvider>
        <ActivityList {...payload} />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(showActivities);
})();
