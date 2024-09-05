import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import FaIcon from "@agir/front/genericComponents/FaIcon";
import Link from "@agir/front/app/Link";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { MailTo } from "@agir/elections/Common/StyledComponents";

import ReplySuccess from "./ReplySuccess";
import AcceptedRequests from "./AcceptedRequests";

import {
  REPLY_ACTION,
  replyToSingleVotingProxyRequest,
  replyToVotingProxyRequests,
} from "@agir/voting_proxies/Common/api";

import voteIcon from "@agir/voting_proxies/Common/images/vote.svg";
import { WarningBlock } from "@agir/elections/Common/StyledComponents";

const StyledFaIcon = styled(FaIcon)``;
const StyledFeatherIcon = styled(RawFeatherIcon)``;
const StyledRecap = styled.div`
  padding: 1rem 1.5rem;
  background-color: ${({ theme }) => theme.background0};
  border-radius: ${({ theme }) => theme.borderRadius};
  border: 1px solid ${({ theme }) => theme.text100};

  & > ${WarningBlock} {
    font-size: 0.875rem;
    margin: 0.5rem -1.5rem;
    padding: 1rem 1.5rem;
  }

  & > h5,
  & > p {
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
  }

  & > p {
    display: flex;
    align-items: start;
    line-height: 1.5;
    gap: 1rem;
    font-size: 0.875rem;

    ${StyledFaIcon},
    ${StyledFeatherIcon} {
      color: ${(props) => props.theme.text500};

      @media (max-width: 350px) {
        display: none;
      }
    }

    ${StyledFaIcon}  {
      padding-left: 0.125rem;
    }

    & > strong {
      text-transform: capitalize;
    }
  }

  & > p + p {
    margin-top: 0.5rem;
  }
`;

const StyledActionRadiusWarning = styled.div`
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
  border-radius: ${(props) => props.theme.borderRadius};
  border: 1px solid ${(props) => props.theme.error500};

  h6,
  p {
    margin: 0;
  }

  h6 {
    color: ${(props) => props.theme.error500};
    font-size: 1.25rem;
    line-height: 1.5;
    display: flex;
    align-items: center;
    gap: 0.5rem 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1rem;
    }

    & > :first-child {
      flex: 0 0 auto;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        display: none;
      }
    }
  }

  p {
    font-size: 0.875rem;

    strong {
      font-size: 1rem;
      font-weight: 700;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        font-size: inherit;
      }
    }
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
    readOnly,
    refreshRequests,
    hasMatchedRequests,
  } = props;

  const [action, setAction] = useState(null);
  const [isAvailable, setIsAvailable] = useState(null);
  const [shouldConfirm, setShouldConfirm] = useState(false);
  const [errors, setErrors] = useState(null);
  const [hasDataSharingConsent, setHasDataSharingConsent] = useState(false);

  const [requests, isSingle] = useMemo(
    () =>
      Array.isArray(props.requests)
        ? [props.requests, false]
        : props.singleRequest
          ? [[props.singleRequest], true]
          : [[], false],
    [props.requests, props.singleRequest],
  );

  const handleChangeDataSharingConsent = useCallback(
    (e) => setHasDataSharingConsent(e.target.checked),
    [],
  );

  const handleSubmit = useCallback(
    async (action) => {
      setErrors(null);
      setAction(action);

      const result = isSingle
        ? await replyToSingleVotingProxyRequest(
            action,
            votingProxyPk,
            requests[0],
          )
        : await replyToVotingProxyRequests(action, votingProxyPk, requests);

      setAction(null);
      setShouldConfirm(false);

      if (result.error?.status === 403) {
        window.location.reload();
      }

      if (result.error) {
        setErrors(result.error);
        return;
      }

      setIsAvailable(action === REPLY_ACTION.ACCEPT);
    },
    [requests, isAvailable, isSingle],
  );

  const acceptRequests = useCallback(
    (e) => {
      e.preventDefault();
      handleSubmit(REPLY_ACTION.ACCEPT);
    },
    [handleSubmit],
  );

  const declineRequests = useCallback(
    (e) => {
      e.preventDefault();
      shouldConfirm
        ? handleSubmit(REPLY_ACTION.DECLINE)
        : setShouldConfirm(true);
    },
    [shouldConfirm, handleSubmit],
  );

  const dismissConfirm = useCallback(() => {
    setShouldConfirm(false);
  }, []);

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
          {firstName}, prenez la procuration de {requests[0].firstName}
        </h2>
        <p>
          {requests[0].firstName} n'est pas disponible pour aller voter pour les
          élections législatives. Vous êtes présent·e ? Prenez sa procuration.
        </p>
      </header>
      <Spacer size="1.5rem" />
      <StyledRecap>
        <h5>Lieu</h5>
        {isSingle && (
          <WarningBlock icon="alert-circle">
            <strong>Attention :</strong> vous devrez vous rendre dans le bureau
            de vote de la personne pour voter à sa place le jour du scrutin !
          </WarningBlock>
        )}
        <Spacer size=".5rem" />
        {requests[0].commune && (
          <p>
            <StyledFeatherIcon name="map-pin" />
            <strong>{requests[0].commune}</strong>
          </p>
        )}
        {requests[0].consulate && (
          <p>
            <StyledFeatherIcon name="map-pin" />
            <strong>{requests[0].consulate}</strong>
          </p>
        )}
        {requests[0].pollingStationLabel && (
          <p>
            <StyledFaIcon icon="booth-curtain:regular" size="1.25rem" />
            <strong>
              Bureau de vote&nbsp;:
              <br />
              {requests[0].pollingStationLabel}
            </strong>
          </p>
        )}
        <Spacer size="1rem" />
        <h5>Date{requests.length > 1 ? "s" : ""}</h5>
        <Spacer size=".5rem" />
        {requests.map((request) => (
          <p key={request.votingDate}>
            <StyledFeatherIcon name="calendar" />
            <strong>{request.votingDate}</strong>
          </p>
        ))}
      </StyledRecap>
      <Spacer size="2rem" />
      <StyledActionRadiusWarning>
        <h6>
          <FaIcon size="2em" icon="face-unamused:regular" />
          Cette proposition de prise de procuration ne vous convient pas&nbsp;?
        </h6>
        <p>
          <strong>
            Vous n'avez rien à faire&nbsp;! Cette demande sera proposée à
            d'autres volontaires et vous recevrez une nouvelle proposition
            lorsqu'une nouvelle demande sera créée près de chez vous.
          </strong>
        </p>
        {requests[0].commune && (
          <p>
            Pour augmenter les chances de répondre à toutes les demandes reçues,
            nous cherchons pour chacune la personne disponible la plus proche{" "}
            <strong>dans un rayon de 20km</strong>. Si ce rayon est trop grand
            pour vous, vous pouvez l'ajuster en modifiant la valeur du champ{" "}
            <strong>zone d'action</strong> sur{" "}
            <Link target="_blank" route="personalInformation">
              la page de votre profil
            </Link>
            .
          </p>
        )}
      </StyledActionRadiusWarning>
      <Spacer size="1.5rem" />
      <form onSubmit={acceptRequests}>
        <CheckboxField
          required
          toggle
          small
          disabled={!!action}
          value={hasDataSharingConsent}
          onChange={handleChangeDataSharingConsent}
          label={`En validant ce formulaire, vous acceptez que ${requests[0].firstName} ait accès à vos informations personnelles necessaires à l'établissement de la procuration de vote (prénom, nom, date de naissance, numéro de téléphone)`}
        />
        {errors && (
          <p
            css={`
              padding: 1rem 0 0;
              margin: 0;
              font-size: 1rem;
              font-weight: 500;
              color: ${({ theme }) => theme.error500};
            `}
          >
            ⚠&ensp;
            {errors.global || "Une erreur est survenue."}
          </p>
        )}
        <Spacer size="1rem" />
        <Button
          wrap
          block
          disabled={!!action}
          loading={action === REPLY_ACTION.ACCEPT}
          type="submit"
          color="success"
        >
          J'accepte de voter pour {requests[0].firstName}
        </Button>
        <Spacer size="1rem" />
        <Button
          wrap
          block
          link
          type="button"
          color="primary"
          route="votingProxyRequestsForProxy"
          routeParams={{ votingProxyPk }}
        >
          Voir d'autres demandes à proximité
        </Button>
        <Spacer size="1rem" />
        <Button
          wrap
          block
          disabled={!!action}
          loading={action === REPLY_ACTION.DECLINE}
          type="button"
          onClick={declineRequests}
        >
          Me retirer de la liste des volontaires
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
        isConfirming={action === REPLY_ACTION.DECLINE}
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
      pollingStationLabel: PropTypes.string.isRequired,
      commune: PropTypes.string,
      consulate: PropTypes.string,
    }),
  ),
  singleRequest: PropTypes.shape({
    id: PropTypes.string.isRequired,
    firstName: PropTypes.string.isRequired,
    votingDate: PropTypes.string.isRequired,
    pollingStationLabel: PropTypes.string.isRequired,
    commune: PropTypes.string,
    consulate: PropTypes.string,
  }),
  readOnly: PropTypes.bool,
  refreshRequests: PropTypes.func,
  hasMatchedRequests: PropTypes.bool,
};
export default ReplyingForm;
