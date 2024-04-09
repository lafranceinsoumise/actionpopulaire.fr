import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import Spacer from "@agir/front/genericComponents/Spacer";

import {
  sendVotingProxyInformation,
  confirmVotingProxyRequests,
  cancelVotingProxyRequests,
} from "@agir/voting_proxies/Common/api";
import { useToast } from "@agir/front/globalContext/hooks";

const StyledWidget = styled.div`
  padding: 1rem 1.5rem;
  background-color: ${({ theme }) => theme.white};
  border-radius: ${({ theme }) => theme.borderRadius};
  border: 1px solid ${({ theme }) => theme.black100};

  & > p > strong {
    font-size: 0.875rem;
    line-height: 1.7;
  }

  ${Button} {
    text-align: left;
    line-height: 1.2;
  }

  footer {
    padding: 1rem 0 0;
    margin: 0;
    font-size: 1rem;
    color: ${({ theme }) => theme.redNSP};
  }
`;

const VotingProxyWidget = (props) => {
  const { request } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isConfirmed, setIsConfirmed] = useState(
    request.status === "confirmed",
  );
  const [isCancelled, setIsCancelled] = useState(
    request.status === "cancelled",
  );
  const [shouldConfirm, setShouldConfirm] = useState(false);

  const sendToast = useToast();

  const dismissConfirm = useCallback(() => {
    setShouldConfirm(false);
  }, []);

  const sendInformation = useCallback(async () => {
    setError("");
    setIsLoading("info");
    const result = await sendVotingProxyInformation([request]);
    setIsLoading(false);
    if (result.error) {
      setError(result.error);
      return;
    }
    sendToast(
      <>
        Les informations de procuration vous ont été envoyées{" "}
        <strong>par SMS et par e-mail</strong>
      </>,
      "SUCCESS",
    );
  }, [request, sendToast]);

  const confirm = useCallback(async () => {
    if (!shouldConfirm) {
      setShouldConfirm("confirm");
      return;
    }
    setError("");
    setIsLoading("confirm");
    const result = await confirmVotingProxyRequests([request]);
    setIsLoading(false);
    setShouldConfirm(false);
    if (result.error) {
      setError(result.error);
      return;
    }
    setIsConfirmed(true);
    sendToast("Votre procuration a bien été validée !", "SUCCESS");
  }, [shouldConfirm, request, sendToast]);

  const cancel = useCallback(async () => {
    if (!shouldConfirm) {
      setShouldConfirm("cancel");
      return;
    }
    setError("");
    setIsLoading("cancel");
    const result = await cancelVotingProxyRequests([request]);
    setIsLoading(false);
    setShouldConfirm(false);
    if (result.error) {
      setError(result.error);
      return;
    }
    setIsCancelled(true);
    sendToast("Votre demande de procuration a bien été annulée !", "SUCCESS");
  }, [shouldConfirm, request, sendToast]);

  return (
    <StyledWidget>
      {request?.votingProxy?.firstName && (
        <p>
          <strong>Prénom(s)&nbsp;:</strong>
          <br />
          {request.votingProxy.firstName}
        </p>
      )}
      <Spacer size="1rem" />
      <p>
        <strong>Scrutin&nbsp;:</strong>
        <br />
        <span>{request.votingDate}</span>
      </p>
      <Spacer size="1rem" />
      <p>
        {!isCancelled && (
          <>
            <Button
              small
              wrap
              block
              disabled={!!isLoading}
              loading={isLoading === "info"}
              onClick={sendInformation}
              icon="message-square"
            >
              Recevoir les informations pour établir la procuration
            </Button>
            <Spacer size=".5rem" />
          </>
        )}
        {!isCancelled && (
          <>
            <Button
              small
              wrap
              block
              link
              disabled={!!isLoading || isConfirmed}
              href="https://www.maprocuration.gouv.fr/"
              target="_blank"
              rel="noopener noreferrer"
              icon="external-link"
            >
              Établir la procuration (sur le site du service public)
            </Button>
            <Spacer size=".5rem" />
          </>
        )}
        {!isCancelled && (
          <>
            <Button
              disabled={!!isLoading || isConfirmed}
              small
              wrap
              block
              color="success"
              onClick={confirm}
              icon="check-square"
            >
              {isConfirmed
                ? "Procuration validée"
                : "Prévenir la personne que la procuration a été établie"}
            </Button>
            <Spacer size=".5rem" />
          </>
        )}
        <Button
          disabled={!!isLoading || isCancelled}
          small
          wrap
          block
          color="danger"
          onClick={cancel}
        >
          {isCancelled
            ? "Procuration annulée"
            : "Annuler la demande de procuration"}
        </Button>
      </p>
      {error && <footer>{error}</footer>}
      <ModalConfirmation
        shouldShow={shouldConfirm === "confirm"}
        onClose={dismissConfirm}
        onConfirm={confirm}
        title={`Prévenir ${request?.votingProxy?.firstName} que vous avez établi la procuration`}
        confirmationLabel="Je confirme que la procuration a été établie"
        dismissLabel="Annuler"
        isConfirming={isLoading === "confirm"}
        shouldDismissOnClick={false}
      >
        <p>
          Après validation, la personne sera prévenue qu'elle pourra se
          présenter à votre bureau de vote pour voter à votre place.
        </p>
      </ModalConfirmation>
      <ModalConfirmation
        shouldShow={shouldConfirm === "cancel"}
        onClose={dismissConfirm}
        onConfirm={cancel}
        title={`Annuler la demande la procuration`}
        confirmationLabel="Je confirme l'annulation de la procuration"
        dismissLabel="Annuler"
        isConfirming={isLoading === "cancel"}
        shouldDismissOnClick={false}
      >
        <p>
          Après validation, la personne sera prévenue et sera disponible pour
          répondre à d'autres demande de procuration.
        </p>
      </ModalConfirmation>
    </StyledWidget>
  );
};
VotingProxyWidget.propTypes = {
  request: PropTypes.object,
};
export default VotingProxyWidget;
