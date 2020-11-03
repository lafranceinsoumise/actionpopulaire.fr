import onDOMReady from "@agir/lib/utils/onDOMReady";
import { DateTime, Interval } from "luxon";
import AgendaPage from "@agir/events/agendaPage/AgendaPage";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: EventCard },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("@agir/front/genericComponents/EventCard"),
    import("@agir/front/genericComponents/GobalContext"),
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
