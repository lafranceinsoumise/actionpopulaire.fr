import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import { useIsDesktop } from "@agir/front/genericComponents/grid";
import AgreementField from "@agir/donations/spendingRequest/common/SpendingRequestAgreement";

import { validateSpendingRequest } from "@agir/donations/spendingRequest/common/api";
import { useToast } from "@agir/front/globalContext/hooks";

const StyledError = styled.p`
  color: ${(props) => props.theme.redNSP};
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

const ValidateSpendingRequestButton = ({ spendingRequest, onValidate }) => {
  const { id, action } = spendingRequest;

  const hasAction = !!action?.label;
  const label = action?.label || "Valider";

  const [isOpen, setIsOpen] = useState(false);
  const [hasAgreement, setHasAgreement] = useState();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const isDesktop = useIsDesktop();
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
    const { error } = await validateSpendingRequest(id);
    setIsLoading(false);
    if (error) {
      return setError(error);
    }
    onValidate();
    sendToast("La demande a bien été validée !", "SUCCESS");
  }, [id, onValidate, sendToast]);

  return (
    <>
      <Button
        small={!isDesktop}
        color="primary"
        icon={hasAction ? "send" : "lock"}
        title={action.explanation}
        disabled={!hasAction}
        onClick={handleOpen}
      >
        {label || "Valider"}
      </Button>
      {hasAction && (
        <ModalConfirmation
          shouldShow={isOpen}
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
              Vous êtes sur le point de valider cette demande de dépense. Une
              fois votre approbation donnée, elle ne sera plus modifiable.
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
      )}
    </>
  );
};

ValidateSpendingRequestButton.propTypes = {
  spendingRequest: PropTypes.shape({
    id: PropTypes.string,
    action: PropTypes.shape({
      label: PropTypes.string,
      explanation: PropTypes.string,
    }),
  }),
  onValidate: PropTypes.func,
};

export default ValidateSpendingRequestButton;
