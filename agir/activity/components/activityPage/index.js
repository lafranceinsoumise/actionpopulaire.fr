import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: ActivityCard },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./ActivityCard"),
    import("@agir/front/genericComponents/GobalContext"),
  ]);

  const showActivities = () => {
    const dataElement = document.getElementById("exportedContent");
    const renderElement = document.getElementById("mainApp");

    if (!dataElement || !renderElement) {
      return;
    }

    const payload = JSON.parse(dataElement.textContent);
    console.log(payload);
    renderReactComponent(
      <GlobalContextProvider>
        <div>
          {payload.data.map(({ id, ...props }) => (
            <ActivityCard key={id} {...props} />
          ))}
        </div>
      </GlobalContextProvider>,
      renderElement
    );
  };
  onDOMReady(showActivities);
})();
