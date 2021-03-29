import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: PushModal },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("../allPages/PushModal"),
    import("@agir/front/globalContext/GlobalContext"),
  ]);

  const showHeader = () => {
    renderReactComponent(
      <GlobalContextProvider>
        <PushModal isActive />
      </GlobalContextProvider>,
      document.getElementById("release-modal")
    );
  };
  onDOMReady(showHeader);
})();
