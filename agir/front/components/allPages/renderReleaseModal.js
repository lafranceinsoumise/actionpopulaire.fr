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
      <ReleaseModal
        isActive={process.env.NODE_ENV === "production"}
        withCookie
      />,
      document.getElementById("release-modal")
    );
  };
  onDOMReady(showHeader);
})();
