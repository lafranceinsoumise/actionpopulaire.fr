import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import ReplySuccess from "./ReplySuccess";

import { replyToVotingProxyRequests } from "@agir/voting_proxies/Common/api";

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

const ReplyingForm = (props) => {
  const { votingProxyPk, firstName, requests } = props;
  const [isAccepting, setIsAccepting] = useState(false);
  const [isDeclining, setIsDeclining] = useState(false);
  const [errors, setErrors] = useState(null);
  const [hasDataSharingConsent, setHasDataSharingConsent] = useState(false);
  const [isAvailable, setIsAvailable] = useState(undefined);

  const isLoading = isAccepting || isDeclining;
  const voter = requests[0];
  const votingProxyRequests = requests.map((r) => r.id);
  const votingDates = requests.map((r) => r.votingDate);

  const handleChangeDataSharingConsent = (e) =>
    setHasDataSharingConsent(e.target.checked);

  const handleSubmit = async (isAvailable) => {
    setErrors(null);
    setIsAccepting(isAvailable);
    setIsDeclining(!isAvailable);
    const result = await replyToVotingProxyRequests(votingProxyPk, {
      votingProxyRequests,
      isAvailable,
    });
    setIsAccepting(false);
    setIsDeclining(false);
    if (result.error) {
      setErrors(result.error);
      return;
    }
    setIsAvailable(isAvailable);
  };

  const acceptRequests = (e) => {
    e.preventDefault();
    handleSubmit(true);
  };

  const declineRequests = (e) => {
    e.preventDefault();
    handleSubmit(false);
  };

  if (typeof isAvailable === "boolean") {
    return <ReplySuccess isAvailable={isAvailable} />;
  }

  return (
    <StyledWrapper>
      <h2>
        {firstName}, prenez la procuration de {voter.firstName}
      </h2>
      <Spacer size="1rem" />
      <p>
        {voter.firstName} n'est pas disponible pour se déplacer lors{" "}
        {requests.length === 1 ? "d'un jour" : "de certains jours"} de vote.
        <br />
        Vous êtes présent·e&nbsp;? <strong>Prenez sa procuration&nbsp;!</strong>
      </p>
      <Spacer size="1.5rem" />
      <StyledRecap>
        <h5>Lieu</h5>
        <Spacer size=".5rem" />
        {voter.commune && (
          <p>
            <RawFeatherIcon name="map-pin" />
            {voter.commune}
          </p>
        )}
        {voter.consulate && (
          <p>
            <RawFeatherIcon name="map-pin" />
            {voter.consulate}
          </p>
        )}
        {voter.pollingStationNumber && (
          <p>
            <RawFeatherIcon name="map-pin" />
            Bureau de vote&nbsp;: {voter.pollingStationNumber}
          </p>
        )}
        <Spacer size="1rem" />
        <h5>Date{requests.length > 1 ? "s" : ""}</h5>
        <Spacer size=".5rem" />
        {votingDates.map((date) => (
          <p key={date}>
            <RawFeatherIcon name="calendar" />
            {date}
          </p>
        ))}
      </StyledRecap>
      <Spacer size="1.5rem" />
      <form onSubmit={acceptRequests}>
        <CheckboxField
          required
          disabled={isLoading}
          value={hasDataSharingConsent}
          onChange={handleChangeDataSharingConsent}
          label={`En validant ce formulaire, vous acceptez que ${voter.firstName} ait accès à vos informations personnelles necessaires à l'établissement de la procuration de vote (prénom, nom, date de naissance, numéro de téléphone)`}
        />
        {errors && (
          <p
            css={`
              padding: 1rem 0 0;
              margin: 0;
              font-size: 1rem;
              font-weight: 500;
              color: ${({ theme }) => theme.redNSP};
            `}
          >
            ⚠&ensp;Une erreur est survenue.
          </p>
        )}
        <Spacer size="1.5rem" />
        <Button
          wrap
          disabled={isLoading}
          loading={isAccepting}
          type="submit"
          color="success"
        >
          J'accepte de voter pour {voter.firstName}
        </Button>
        <Spacer size="1rem" />
        <Button
          wrap
          disabled={isLoading}
          loading={isDeclining}
          type="button"
          onClick={declineRequests}
        >
          Je ne suis plus disponible
        </Button>
      </form>
    </StyledWrapper>
  );
};
ReplyingForm.propTypes = {
  votingProxyPk: PropTypes.string.isRequired,
  firstName: PropTypes.string.isRequired,
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
};
export default ReplyingForm;