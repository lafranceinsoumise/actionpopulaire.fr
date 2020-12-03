import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: FeedbackButton },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./FeedbackButton"),
    import("../genericComponents/GlobalContext"),
  ]);

  const showHeader = () => {
    renderReactComponent(
      <GlobalContextProvider>
        <FeedbackButton />
      </GlobalContextProvider>,
      document.getElementById("feedback-button")
    );
  };
  onDOMReady(showHeader);
})();
