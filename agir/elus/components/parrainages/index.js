import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: App },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./App"),
    import("@agir/front/globalContext/GlobalContext"),
  ]);

  const displayInterface = () => {
    const elusProchesScript = document.getElementById("elusProches");
    let elusProchesData = [];

    if (elusProchesScript && elusProchesScript.type === "application/json") {
      elusProchesData = JSON.parse(elusProchesScript.textContent);
    }

    renderReactComponent(
      <GlobalContextProvider>
        <App elusProches={elusProchesData} />
      </GlobalContextProvider>,
      document.getElementById("app")
    );
  };
  onDOMReady(displayInterface);
})();
