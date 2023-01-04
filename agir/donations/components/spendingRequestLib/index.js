import React from "react";
import onDOMReady from "@agir/lib/utils/onDOMReady";
import DeleteSpendingRequest from "@agir/donations/spendingRequestLib/DeleteSpendingRequest";
import DeleteDocumentButton from "@agir/donations/spendingRequestLib/DeleteDocumentButton";
import { renderReactComponent } from "@agir/lib/utils/react";

function render() {
  for (let spendingRequestDelete of document.querySelectorAll(
    ".delete-spending-request"
  )) {
    renderReactComponent(
      <DeleteSpendingRequest {...spendingRequestDelete.dataset} />,
      spendingRequestDelete
    );
  }
  for (let documentDelete of document.querySelectorAll(".delete-document")) {
    renderReactComponent(
      <DeleteDocumentButton {...documentDelete.dataset} />,
      documentDelete
    );
  }
}

onDOMReady(render);
