import "core-js/stable";
import "regenerator-runtime/runtime";
import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { default: ReactDOM },
    { default: DeleteDocumentButton },
  ] = await Promise.all([
    import("react"),
    import("react-dom"),
    import("./DeleteDocumentButton"),
  ]);

  function render() {
    for (let documentDelete of document.querySelectorAll(".delete-document")) {
      ReactDOM.render(
        <DeleteDocumentButton {...documentDelete.dataset} />,
        documentDelete
      );
    }
  }

  onDOMReady(render);
})();
