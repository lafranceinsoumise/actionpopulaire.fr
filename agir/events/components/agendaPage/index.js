import onDOMReady from "@agir/lib/utils/onDOMReady";
import AgendaPage from "@agir/events/agendaPage/AgendaPage";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("@agir/front/globalContext/GlobalContext"),
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
        <AgendaPage {...payload} />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(showActivities);
})();
