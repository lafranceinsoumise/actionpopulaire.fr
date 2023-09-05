import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";
import { deleteSpendingRequest } from "@agir/donations/spendingRequest/common/api";
import { useBackLink } from "@agir/front/app/Navigation/BackLink/BackLink";
import AppRedirect from "@agir/front/app/Redirect";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledError = styled.p`
  color: ${(props) => props.theme.redNSP};
  text-align: center;
  font-weight: 500;

  &:empty {
    display: none;
  }
`;

const StyledModalContent = styled.div`
  display: flex;
  flex-flow: column nowrap;
  padding: 1rem 0 0;
  gap: 1rem;

  & > * {
    margin: 0;
  }

  p strong {
    font-weight: 600;
  }
`;

const DeleteSpendingRequestButton = ({ spendingRequest, disabled }) => {
  const { id, title, group } = spendingRequest;

  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDeleted, setIsDeleted] = useState(false);

  const isDesktop = useIsDesktop();
  const redirectTo = useMemo(
    () =>
      group
        ? {
            label: "Gestion du groupe",
            route: "groupSettings",
            routeParams: {
              groupPk: group.id,
              activePanel: "finance",
            },
          }
        : undefined,
    [group]
  );

  useBackLink(redirectTo);

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
    const { error } = await deleteSpendingRequest(id);
    setIsLoading(false);
    error ? setError(error) : setIsDeleted(true);
  }, [id]);

  if (isDeleted) {
    return (
      <AppRedirect {...redirectTo} toast="La demande a bien été supprimée !" />
    );
  }

  return (
    <>
      <Button
        disabled={disabled || isLoading}
        small={!isDesktop}
        color="choose"
        icon="trash-2"
        onClick={handleOpen}
        loading={isLoading}
        title={disabled ? "Cette demande ne peut pas être supprimée" : ""}
      >
        Supprimer
      </Button>
      <ModalConfirmation
        shouldShow={isOpen}
        onClose={!isLoading && !isDeleted ? handleClose : undefined}
        title="Supprimer la demande de dépense"
        dismissLabel="Annuler"
        confirmationLabel="Supprimer la demande"
        onConfirm={handleConfirm}
        shouldDismissOnClick={false}
      >
        <StyledModalContent>
          <p>
            Confirmez-vous la suppression définitive{" "}
            {title ? (
              <>
                de la demande <mark>{title}</mark>
              </>
            ) : (
              "de cette demande"
            )}
            &nbsp;?
          </p>
          <p>
            <strong>
              ⚠&ensp;Attention&nbsp;: cette action est irréversible.
            </strong>
          </p>
          <StyledError>{error}</StyledError>
        </StyledModalContent>
      </ModalConfirmation>
    </>
  );
};

DeleteSpendingRequestButton.propTypes = {
  spendingRequest: PropTypes.shape({
    id: PropTypes.string,
    title: PropTypes.string,
    group: PropTypes.shape({
      id: PropTypes.string,
    }),
  }),
  disabled: PropTypes.bool,
};

export default DeleteSpendingRequestButton;
