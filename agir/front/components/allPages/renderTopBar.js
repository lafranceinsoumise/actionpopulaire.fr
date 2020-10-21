import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { default: ReactDOM },
    { default: TopBar },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("react-dom"),
    import("./TopBar"),
    import("../genericComponents/GobalContext"),
  ]);

  const showHeader = () => {
    ReactDOM.render(
      <GlobalContextProvider>
        <TopBar />
      </GlobalContextProvider>,
      document.getElementById("top-bar")
    );
  };
  onDOMReady(showHeader);
})();
