import PropTypes from "prop-types";
import React, { useCallback, useRef, useState } from "react";

import { getCookie } from "@agir/lib/utils/cookies";

import Button from "@agir/lib/bootstrap/Button";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";

const DeleteDocumentButton = ({ deleteUrl, documentName }) => {
  const deleteForm = useRef();
  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = useCallback(() => {
    setIsOpen(true);
  }, []);

  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  const handleConfirm = useCallback(() => {
    deleteForm.current && deleteForm.current.submit();
  }, []);

  return (
    <>
      <Button
        bsSize="sm"
        bsStyle="danger"
        onClick={handleOpen}
        title="Supprimer le document"
      >
        <span className="fa fa-trash" />
      </Button>
      <ModalConfirmation
        shouldShow={isOpen}
        onClose={handleClose}
        title={`Supprimer le document ${documentName}`}
        dismissLabel="Annuler"
        confirmationLabel="Supprimer le document"
        onConfirm={handleConfirm}
        shouldDismissOnClick
      >
        <form ref={deleteForm} method="post" action={deleteUrl}>
          <input
            type="hidden"
            name="csrfmiddlewaretoken"
            value={getCookie("csrftoken")}
          />
          <p>Confirmez-vous la suppression définitive de ce document&nbsp;?</p>
          <p>Attention&nbsp;: cette action est irréversible.</p>
        </form>
      </ModalConfirmation>
    </>
  );
};

DeleteDocumentButton.propTypes = {
  deleteUrl: PropTypes.string,
  documentName: PropTypes.string,
};

export default DeleteDocumentButton;
