import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";

const StyledError = styled.p`
  color: ${(props) => props.theme.redNSP};
  text-align: center;
  font-weight: 500;

  &:empty {
    display: none;
  }
`;

const StyledWarning = styled.p`
  color: ${(props) => props.theme.vermillon};
  font-weight: 600;
  font-size: 0.875rem;
`;

const StyledModalContent = styled.div`
  display: flex;
  flex-flow: column nowrap;
  padding: 1rem 0 0;
  gap: 1rem;

  & > * {
    margin: 0;
  }
`;

const DeleteAttachmentModalConfirmation = (props) => {
  const { attachment, isLoading, onConfirm, onClose, error } = props;

  const handleConfirm = useCallback(() => {
    onConfirm(attachment.id);
  }, [onConfirm, attachment]);

  return (
    <ModalConfirmation
      shouldShow={!!attachment}
      onClose={!isLoading ? onClose : undefined}
      title="Supprimer le document"
      dismissLabel="Annuler"
      confirmationLabel="Supprimer le document"
      onConfirm={handleConfirm}
      shouldDismissOnClick={false}
    >
      <StyledModalContent>
        <p>
          Confirmez-vous la suppression du document&nbsp;:{" "}
          <mark>{attachment?.title}</mark>&nbsp;?
        </p>
        <StyledWarning>
          ⚠&ensp;Attention&nbsp;: cette action est irréversible&nbsp;!
        </StyledWarning>
        <StyledError>{error}</StyledError>
      </StyledModalContent>
    </ModalConfirmation>
  );
};

DeleteAttachmentModalConfirmation.propTypes = {
  attachment: PropTypes.object,
  isLoading: PropTypes.bool,
  onConfirm: PropTypes.func,
  onClose: PropTypes.func,
  error: PropTypes.string,
};

export default DeleteAttachmentModalConfirmation;
