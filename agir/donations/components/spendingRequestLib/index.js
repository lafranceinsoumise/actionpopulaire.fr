import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: DeleteDocumentButton },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./DeleteDocumentButton"),
  ]);

  function render() {
    for (let documentDelete of document.querySelectorAll(".delete-document")) {
      renderReactComponent(
        <DeleteDocumentButton {...documentDelete.dataset} />,
        documentDelete
      );
    }
  }

  onDOMReady(render);
})();
