import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { GlobalContextProvider },
    { default: EventPage },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("@agir/front/genericComponents/GobalContext"),
    import("./EventPage"),
  ]);

  const render = () => {
    const dataElement = document.getElementById("exportedEvent");
    const renderElement = document.getElementById("mainApp");

    if (!dataElement || !renderElement) {
      console.log("Pas d'événement à présenter");
      return;
    }

    const data = JSON.parse(dataElement.textContent);
    renderReactComponent(
      <GlobalContextProvider>
        <EventPage {...data} />
      </GlobalContextProvider>,
      renderElement
    );
  };

  onDOMReady(render);
})();
