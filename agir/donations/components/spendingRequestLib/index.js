import React from "react";
import ReactDOM from "react-dom";
import DeleteDocumentButton from "donations/spendingRequestLib/DeleteDocumentButton";

for (let documentDelete of document.querySelectorAll(".delete-document")) {
  ReactDOM.render(
    <DeleteDocumentButton {...documentDelete.dataset} />,
    documentDelete
  );
}
