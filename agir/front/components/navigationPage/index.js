import onDOMReady from "@agir/lib/utils/onDOMReady";
import NavigationPage from "./NavigationPage";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("@agir/front/genericComponents/GobalContext"),
  ]);

  const init = () => {
    const dataElement = document.getElementById("exportedContent");
    const renderElement = document.getElementById("mainApp");

    if (!dataElement || !renderElement) {
      return;
    }

    const payload = JSON.parse(dataElement.textContent);
    renderReactComponent(
      <GlobalContextProvider>
        <NavigationPage {...payload} />
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(init);
})();
