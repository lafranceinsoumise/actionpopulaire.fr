import "core-js/stable";
import "regenerator-runtime/runtime";
import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { default: ReactDOM },
    { GlobalContextProvider },
    { default: EventPage },
  ] = await Promise.all([
    import("react"),
    import("react-dom"),
    import("@agir/front/genericComponents/GobalContext"),
    import("./EventPage"),
  ]);

  const render = () => {
    const data = JSON.parse(
      document.getElementById("exportedEvent").textContent
    );
    ReactDOM.render(
      <GlobalContextProvider>
        <EventPage {...data} />
      </GlobalContextProvider>,
      document.getElementById("mainApp")
    );
  };

  onDOMReady(render);
})();
