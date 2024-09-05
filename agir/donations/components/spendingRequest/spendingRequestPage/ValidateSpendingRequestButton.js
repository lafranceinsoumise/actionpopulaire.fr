import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import AgreementField from "@agir/donations/spendingRequest/common/SpendingRequestAgreement";

import { validateSpendingRequest } from "@agir/donations/spendingRequest/common/api";
import { useToast } from "@agir/front/globalContext/hooks";

const StyledError = styled.p`
  color: ${(props) => props.theme.error500};
  text-align: center;
  font-weight: 500;

  &:empty {
    display: none;
  }
`;

const StyledModalTitle = styled.span`
  display: block;
  font-size: 0.875rem;
  text-align: center;
  color: ${(props) => props.theme.primary500};
  text-transform: uppercase;
  font-weight: 700;
`;

const StyledModalContent = styled.div`
  display: flex;
  flex-flow: column nowrap;
  padding: 1rem 0 1rem;
  gap: 1rem;

  & > * {
    margin: 0;
  }

  p strong {
    font-weight: 600;
  }
`;

const ValidateSpendingRequestButton = ({
  spendingRequestPk,
  action,
  onValidate,
}) => {
  const hasAction = !!action;
  const label = action || "Valider";

  const [isOpen, setIsOpen] = useState(false);
  const [hasAgreement, setHasAgreement] = useState();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendToast = useToast();

  const handleOpen = useCallback(() => {
    setIsOpen(true);
  }, []);

  const handleClose = useCallback(() => {
    setError(false);
    setIsOpen(false);
  }, []);

  const handleConfirm = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    const { error } = await validateSpendingRequest(spendingRequestPk);
    setIsLoading(false);
    if (error) {
      return setError(error);
    }
    setIsOpen(false);
    onValidate();
    sendToast("La demande a bien été validée !", "SUCCESS");
  }, [spendingRequestPk, onValidate, sendToast]);

  return (
    <>
      <Button
        color="success"
        icon="arrow-right"
        disabled={!hasAction}
        onClick={handleOpen}
      >
        {label || "Valider"}
      </Button>
      <ModalConfirmation
        shouldShow={hasAction && isOpen}
        onClose={!isLoading ? handleClose : undefined}
        title={<StyledModalTitle>Attention</StyledModalTitle>}
        dismissLabel="Annuler"
        confirmationLabel={label}
        onConfirm={handleConfirm}
        shouldDismissOnClick={false}
        disabled={!hasAgreement}
        isConfirming={isLoading}
      >
        <StyledModalContent>
          <p>
            Vous êtes sur le point de valider cette demande de dépense. Une fois
            votre approbation donnée, elle ne sera plus modifiable.
          </p>
          <p>
            <AgreementField
              onChange={setHasAgreement}
              disabled={isLoading}
              reset={isOpen}
            />
          </p>
          <StyledError>{error?.detail}</StyledError>
        </StyledModalContent>
      </ModalConfirmation>
    </>
  );
};

ValidateSpendingRequestButton.propTypes = {
  spendingRequestPk: PropTypes.string,
  action: PropTypes.string,
  onValidate: PropTypes.func,
};

export default ValidateSpendingRequestButton;
