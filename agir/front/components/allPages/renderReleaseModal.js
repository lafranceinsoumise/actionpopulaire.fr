import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: ReleaseModal },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./ReleaseModal"),
    import("@agir/front/genericComponents/GlobalContext"),
  ]);

  const showHeader = () => {
    renderReactComponent(
      <GlobalContextProvider>
        <ReleaseModal once />
      </GlobalContextProvider>,
      document.getElementById("release-modal")
    );
  };
  onDOMReady(showHeader);
})();
