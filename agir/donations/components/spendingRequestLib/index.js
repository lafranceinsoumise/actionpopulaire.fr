import React from "react";
import onDOMReady from "@agir/lib/utils/onDOMReady";
import DeleteDocumentButton from "@agir/donations/spendingRequestLib/DeleteDocumentButton";
import { renderReactComponent } from "@agir/lib/utils/react";

function render() {
  for (let documentDelete of document.querySelectorAll(".delete-document")) {
    renderReactComponent(
      <DeleteDocumentButton {...documentDelete.dataset} />,
      documentDelete
    );
  }
}

onDOMReady(render);
