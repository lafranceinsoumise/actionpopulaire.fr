import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import FaIcon from "@agir/front/genericComponents/FaIcon";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { MailTo } from "@agir/elections/Common/StyledComponents";

import ReplySuccess from "./ReplySuccess";
import AcceptedRequests from "./AcceptedRequests";

import { replyToVotingProxyRequests } from "@agir/voting_proxies/Common/api";

import voteIcon from "@agir/voting_proxies/Common/images/vote.svg";

const StyledRecap = styled.div`
  padding: 1rem 1.5rem;
  background-color: ${({ theme }) => theme.white};
  border-radius: ${({ theme }) => theme.borderRadius};
  border: 1px solid ${({ theme }) => theme.black100};

  h5,
  p {
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
  }

  p {
    display: flex;
    align-items: start;
    line-height: 1.5;
    gap: 1rem;

    ${FaIcon},
    ${RawFeatherIcon} {
      color: ${(props) => props.theme.black500};

      @media (max-width: 350px) {
        display: none;
      }
    }

    & > strong {
      text-transform: capitalize;
    }
  }

  p + p {
    margin-top: 0.5rem;
  }
`;

const StyledWrapper = styled.div`
  header {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.5rem 1.5rem;
    padding: 1rem 1.5rem;
    background-color: ${(props) => props.theme.primary50};
    border-radius: ${(props) => props.theme.borderRadius};

    img {
      grid-column: 1 / 2;
      grid-row: span 2;
      align-self: center;
    }

    h2,
    p {
      grid-column: 2/3;
      grid-row: span 1;

      &::first-letter {
        text-transform: capitalize;
      }
    }
  }

  footer {
    display: flex;
    gap: 1rem;
  }
`;

const ReplyingForm = (props) => {
  const {
    votingProxyPk,
    firstName,
    requests,
    readOnly,
    refreshRequests,
    hasMatchedRequests,
  } = props;
  const [isAccepting, setIsAccepting] = useState(false);
  const [shouldConfirm, setShouldConfirm] = useState(false);
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
    if (!isAvailable && !shouldConfirm) {
      setShouldConfirm(true);
      return;
    }
    setErrors(null);
    setIsAccepting(isAvailable);
    setIsDeclining(!isAvailable);
    const result = await replyToVotingProxyRequests(votingProxyPk, {
      votingProxyRequests,
      isAvailable,
    });
    setIsAccepting(false);
    setIsDeclining(false);
    setShouldConfirm(false);
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

  const dismissConfirm = () => {
    setShouldConfirm(false);
  };

  if (typeof isAvailable === "boolean") {
    return <ReplySuccess isAvailable={isAvailable} />;
  }

  if (Array.isArray(requests) && requests.length > 0 && readOnly) {
    return (
      <>
        <AcceptedRequests
          requests={requests}
          refreshRequests={refreshRequests}
          hasMatchedRequests={hasMatchedRequests}
        />
        <Spacer size="2rem" />
        <MailTo />
      </>
    );
  }

  return (
    <StyledWrapper>
      <header>
        <img src={voteIcon} width="60" height="60" />
        <h2>
          {firstName}, prenez la procuration de {voter.firstName}
        </h2>
        <p>
          {voter.firstName} n'est pas disponible pour aller voter le 9 juin
          prochain pour les élections européennes. Vous êtes présent·e ? Prenez
          sa procuration.
        </p>
      </header>
      <Spacer size="1.5rem" />
      <StyledRecap>
        <h5>Lieu</h5>
        <Spacer size=".5rem" />
        {voter.commune && (
          <p>
            <RawFeatherIcon name="map-pin" />
            <strong>{voter.commune}</strong>
          </p>
        )}
        {voter.consulate && (
          <p>
            <RawFeatherIcon name="map-pin" />
            <strong>{voter.consulate}</strong>
          </p>
        )}
        {voter.pollingStationNumber && (
          <p>
            <FaIcon icon="booth-curtain:regular" size="1.5rem" />
            <strong>Bureau de vote&nbsp;: {voter.pollingStationNumber}</strong>
          </p>
        )}
        <Spacer size="1rem" />
        <h5>Date{requests.length > 1 ? "s" : ""}</h5>
        <Spacer size=".5rem" />
        {votingDates.map((date) => (
          <p key={date}>
            <RawFeatherIcon name="calendar" />
            <strong>{date}</strong>
          </p>
        ))}
      </StyledRecap>
      <Spacer size="0.5rem" />
      <Spacer size="1.5rem" />
      <div
        css={`
          display: flex;
          align-items: start;
          gap: 1rem;

          & > :first-child {
            flex: 0 0 auto;
            color: ${(props) => props.theme.primary500};
          }
        `}
      >
        <RawFeatherIcon name="arrow-right" />
        <p>
          <strong>
            Cette proposition de prise de procuration ne vous convient
            pas&nbsp;?
          </strong>
          <br />
          Vous n'avez rien à faire&nbsp;! Vous recevrez une nouvelle proposition
          lorsqu'une nouvelle demande sera créée près de chez vous.
        </p>
      </div>
      <Spacer size="1.5rem" />
      <form onSubmit={acceptRequests}>
        <CheckboxField
          required
          toggle
          small
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
            ⚠&ensp;{errors?.global || "Une erreur est survenue."}
          </p>
        )}
        <Spacer size="1rem" />
        <Button
          wrap
          block
          disabled={isLoading || !!errors?.global}
          loading={isAccepting}
          type="submit"
          color="success"
        >
          J'accepte de voter pour {voter.firstName}
        </Button>
        <Spacer size="1rem" />
        <Button
          wrap
          block
          disabled={isLoading}
          loading={isDeclining}
          type="button"
          onClick={declineRequests}
        >
          Je ne suis plus disponible (me retirer de la liste des volontaires)
        </Button>
      </form>
      <Spacer size="2rem" />
      <MailTo />
      <ModalConfirmation
        shouldShow={shouldConfirm}
        onClose={dismissConfirm}
        onConfirm={declineRequests}
        title="Ne plus recevoir de proposition de prise de procuration"
        confirmationLabel="Confirmer"
        dismissLabel="Annuler"
        isConfirming={isDeclining}
        shouldDismissOnClick={false}
      >
        <p>
          Souhaitez-vous ne plus être volontaire pour prendre des
          procurations&nbsp;? Nous ne vous enverrons plus de message lorsqu'une
          demande de procuration sera créée près de chez vous.
        </p>
      </ModalConfirmation>
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
    }),
  ).isRequired,
  readOnly: PropTypes.bool,
  refreshRequests: PropTypes.func,
  hasMatchedRequests: PropTypes.bool,
};
export default ReplyingForm;
