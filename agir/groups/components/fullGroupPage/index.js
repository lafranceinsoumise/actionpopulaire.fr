import onDOMReady from "@agir/lib/utils/onDOMReady";
import FullGroupPage from "@agir/groups/fullGroupPage/FullGroupPage";

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
        <FullGroupPage {...payload} />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(showActivities);
})();
