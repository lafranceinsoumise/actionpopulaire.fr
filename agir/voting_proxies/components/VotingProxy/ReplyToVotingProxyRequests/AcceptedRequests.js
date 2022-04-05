import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { confirmVotingProxyRequests } from "@agir/voting_proxies/Common/api";

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
  const isSelectable = request.status === "accepted";
  const handleSelect = isSelectable ? () => selectRequest(request) : undefined;

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
            small
            wrap
            icon={!isSelectable ? "check" : undefined}
            color="primary"
            disabled={!isSelectable || isLoading}
            loading={isLoading}
            type="button"
            onClick={handleSelect}
          >
            {isSelectable
              ? "Confirmer l'établissement de la procuration"
              : "Procuration confirmée"}
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
  const { requests, refreshRequests } = props;
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState(null);

  const confirmRequest = async () => {
    setErrors(null);
    setIsLoading(true);
    const result = await confirmVotingProxyRequests([selectedRequest]);
    setIsLoading(false);
    if (result.error) {
      setErrors(result.error);
      return;
    }
    setSelectedRequest(null);
    refreshRequests && refreshRequests();
  };

  const dismissConfirm = () => {
    setSelectedRequest(null);
  };

  return (
    <StyledWrapper>
      <h2>Mes procurations de vote</h2>
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
          selectRequest={setSelectedRequest}
          isLoading={isLoading}
        />
      ))}
      <ModalConfirmation
        shouldShow={!!selectedRequest}
        onClose={dismissConfirm}
        onConfirm={confirmRequest}
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
};
export default AcceptedRequests;
