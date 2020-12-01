import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: ReleaseModal },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./ReleaseModal"),
  ]);

  const showHeader = () => {
    renderReactComponent(
      <ReleaseModal once />,
      document.getElementById("release-modal")
    );
  };
  onDOMReady(showHeader);
})();
