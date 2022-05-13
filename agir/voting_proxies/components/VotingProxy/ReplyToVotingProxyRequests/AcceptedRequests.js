import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import StaticToast from "@agir/front/genericComponents/StaticToast";

import {
  confirmVotingProxyRequests,
  cancelVotingProxyRequests,
  cancelVotingProxyRequestAcceptation,
} from "@agir/voting_proxies/Common/api";

const StyledRecap = styled.div`
  padding: 1rem 1.5rem;
  background-color: ${({ theme }) => theme.primary50};
  border-radius: ${({ theme }) => theme.borderRadius};

  h5,
  p {
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;

    ${RawFeatherIcon} {
      flex: 0 0 auto;
      width: 0.875rem;
      height: 0.875rem;
      margin-right: 0.5rem;

      @media (max-width: 350px) {
        display: none;
      }
    }
  }

  p > span {
    color: ${({ theme }) => theme.primary500};
  }

  p > strong {
    text-transform: capitalize;
  }

  p + p {
    margin-top: 0.5rem;
  }
`;

const StyledWrapper = styled.div`
  h2,
  p {
    ::first-letter {
      text-transform: capitalize;
    }
  }

  h2 {
    color: ${({ theme }) => theme.primary500};
  }

  footer {
    display: flex;
    gap: 1rem;
  }
`;

const AcceptedRequest = (props) => {
  const { request, selectRequest, isLoading } = props;
  const isConfirmed = request.status === "confirmed";
  const handleConfirm = !isConfirmed
    ? () => selectRequest(request, "confirm")
    : undefined;
  const handleCancel = () => selectRequest(request, "cancel");
  const handleCancelAcceptation = () =>
    selectRequest(request, "cancelAcceptation");

  return (
    <>
      <Spacer size="1rem" />
      <StyledRecap>
        <p>
          Voter pour&nbsp;:&nbsp;<strong>{request.firstName}</strong>
        </p>
        <p>
          <RawFeatherIcon name="calendar" />
          {request.votingDate}
        </p>
        <p>
          <RawFeatherIcon name="map-pin" />
          {request.commune || request.consulate}
        </p>
        <Spacer size="1rem" />
        <p>
          <Button
            block
            small
            wrap
            icon={isConfirmed ? "check" : undefined}
            color="primary"
            disabled={isConfirmed || isLoading}
            loading={isLoading}
            type="button"
            onClick={handleConfirm}
          >
            {isConfirmed
              ? "Procuration confirmée"
              : "Je confirme l'établissement de la procuration"}
          </Button>
        </p>
        <p>
          <Button
            block
            small
            wrap
            disabled={isLoading}
            loading={isLoading}
            type="button"
            onClick={handleCancel}
          >
            La personne n'a plus besoin de procuration
          </Button>
        </p>
        <p>
          <Button
            block
            small
            wrap
            disabled={isLoading}
            loading={isLoading}
            type="button"
            onClick={handleCancelAcceptation}
          >
            Je ne suis plus disponible
          </Button>
        </p>
      </StyledRecap>
    </>
  );
};
AcceptedRequest.propTypes = {
  request: PropTypes.shape({
    id: PropTypes.string.isRequired,
    firstName: PropTypes.string.isRequired,
    votingDate: PropTypes.string.isRequired,
    pollingStationNumber: PropTypes.string.isRequired,
    commune: PropTypes.string,
    consulate: PropTypes.string,
    status: PropTypes.string,
  }),
  selectRequest: PropTypes.func,
  isLoading: PropTypes.bool,
};

const AcceptedRequests = (props) => {
  const { requests, refreshRequests, hasMatchedRequests } = props;
  const [selectedAction, setSelectedAction] = useState(null);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState(null);

  const actOnRequest = async () => {
    if (!selectedAction || !selectRequest) {
      setSelectedRequest(null);
      setSelectedAction(null);
      return;
    }
    setErrors(null);
    setIsLoading(true);
    const f =
      selectedAction === "confirm"
        ? confirmVotingProxyRequests
        : selectedAction === "cancel"
        ? cancelVotingProxyRequests
        : cancelVotingProxyRequestAcceptation;
    const result = await f([selectedRequest]);
    setIsLoading(false);
    if (result.error) {
      setErrors(result.error);
      return;
    }
    setSelectedRequest(null);
    setSelectedAction(null);
    refreshRequests && refreshRequests();
  };

  const dismissConfirm = () => {
    setSelectedRequest(null);
    setSelectedAction(null);
  };

  const selectRequest = (request, action) => {
    setSelectedRequest(request);
    setSelectedAction(action);
  };

  return (
    <StyledWrapper>
      <h2>Mes procurations de vote</h2>
      {hasMatchedRequests && (
        <StaticToast style={{ marginTop: "1rem" }}>
          Cette demande de procuration a été déjà acceptée par quelqu'un d'autre
          ou a été annulée.
          <br />
          Nous vous recontacterons dès qu'une nouvelle personne aura demandé une
          procuration.
        </StaticToast>
      )}
      <Spacer size="1rem" />
      <p>
        Vous avez déjà accepté les procurations suivantes. Vérifiez vos SMS
        et/ou emails pour y retrouver toutes les informations.
      </p>
      <Spacer size="1rem" />
      {requests.map((request) => (
        <AcceptedRequest
          key={request.id}
          request={request}
          selectRequest={selectRequest}
          isLoading={isLoading}
        />
      ))}
      <ModalConfirmation
        shouldShow={!!selectedRequest && !!selectedAction}
        onClose={dismissConfirm}
        onConfirm={actOnRequest}
        title="Confirmer l'établissement de la procuration par le mandant"
        confirmationLabel="Je confirme"
        dismissLabel="Annuler"
        isConfirming={isLoading}
        shouldDismissOnClick={false}
      >
        <p>
          Le mandant doit établir une procuration de vote à votre nom pour cette
          date dans un commissariat de police, une brigade de gendarmerie ou un
          consulat.
        </p>
        <p>
          Confirmez-vous que tout est prêt pour que vous puissiez voter à sa
          place le jour du scrutin&nbsp;?
        </p>
        {errors && (
          <p
            css={`
              padding: 0;
              margin: 0;
              font-size: 1rem;
              font-weight: 500;
              color: ${({ theme }) => theme.redNSP};
              text-align: center;
            `}
          >
            {errors?.votingProxyRequests ||
              errors?.global ||
              "Une erreur est survenue"}
          </p>
        )}
      </ModalConfirmation>
      <ModalConfirmation
        shouldShow={!!selectedRequest && selectedAction === "confirm"}
        onClose={dismissConfirm}
        onConfirm={actOnRequest}
        title="Confirmer l'établissement de la procuration par le mandant"
        confirmationLabel="Je confirme"
        dismissLabel="Annuler"
        isConfirming={isLoading}
        shouldDismissOnClick={false}
      >
        <p>
          Le mandant doit établir une procuration de vote à votre nom pour cette
          date dans un commissariat de police, une brigade de gendarmerie ou un
          consulat.
        </p>
        <p>
          Confirmez-vous que tout est prêt pour que vous puissiez voter à sa
          place le jour du scrutin&nbsp;?
        </p>
        {errors && (
          <p
            css={`
              padding: 0;
              margin: 0;
              font-size: 1rem;
              font-weight: 500;
              color: ${({ theme }) => theme.redNSP};
              text-align: center;
            `}
          >
            {errors?.votingProxyRequests ||
              errors?.global ||
              "Une erreur est survenue"}
          </p>
        )}
      </ModalConfirmation>
      <ModalConfirmation
        shouldShow={!!selectedRequest && selectedAction === "cancel"}
        onClose={dismissConfirm}
        onConfirm={actOnRequest}
        title="Confirmer l'annulation de la procuration par le mandant"
        confirmationLabel="Je confirme"
        dismissLabel="Annuler"
        isConfirming={isLoading}
        shouldDismissOnClick={false}
      >
        <p>
          En annulant la procuration, vous indiquez que la personne qui en a
          fait la demande n'a plus besoin qu'on vote à sa place ou est dans
          l'impossibilité de valider sa demande. Sa demande sera annulée et ne
          sera plus reproposée à un·e volontaire.
        </p>
        <p>
          Confirmez-vous que le mandant vous a communiqué ne plus avoir besoin
          de vous donner procuration pour ce scrutin&nbsp;?
        </p>
        {errors && (
          <p
            css={`
              padding: 0;
              margin: 0;
              font-size: 1rem;
              font-weight: 500;
              color: ${({ theme }) => theme.redNSP};
              text-align: center;
            `}
          >
            {errors?.votingProxyRequests ||
              errors?.global ||
              "Une erreur est survenue"}
          </p>
        )}
      </ModalConfirmation>
      <ModalConfirmation
        shouldShow={!!selectedRequest && selectedAction === "cancelAcceptation"}
        onClose={dismissConfirm}
        onConfirm={actOnRequest}
        title="Se désister de cette procuration de vote"
        confirmationLabel="Je confirme"
        dismissLabel="Annuler"
        isConfirming={isLoading}
        shouldDismissOnClick={false}
      >
        <p>
          En vous désistant de cette procuration, vous indiquez que vous n'êtes
          plus disponible pour voter à la place de cette personne le jour du
          scrutin. Votre acceptation sera annulée et cette demande proposée à
          d'autres personnes.
        </p>
        <p>
          Confirmez-vous que ne pas pouvoir satisfaire cette demande de
          procuration&nbsp;?
        </p>
        {errors && (
          <p
            css={`
              padding: 0;
              margin: 0;
              font-size: 1rem;
              font-weight: 500;
              color: ${({ theme }) => theme.redNSP};
              text-align: center;
            `}
          >
            {errors?.votingProxyRequests ||
              errors?.global ||
              "Une erreur est survenue"}
          </p>
        )}
      </ModalConfirmation>
    </StyledWrapper>
  );
};
AcceptedRequests.propTypes = {
  votingProxyPk: PropTypes.string.isRequired,
  requests: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      firstName: PropTypes.string.isRequired,
      votingDate: PropTypes.string.isRequired,
      pollingStationNumber: PropTypes.string.isRequired,
      commune: PropTypes.string,
      consulate: PropTypes.string,
    })
  ).isRequired,
  refreshRequests: PropTypes.func,
  hasMatchedRequests: PropTypes.bool,
};
export default AcceptedRequests;
