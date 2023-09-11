import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";
import AttachmentList, {
  AttachmentItem,
} from "@agir/donations/spendingRequest/common/AttachmentList";
import CategoryCard from "@agir/donations/spendingRequest/common/CategoryCard";
import Card from "@agir/front/genericComponents/Card";
import Spacer from "@agir/front/genericComponents/Spacer";

import { TIMING_OPTIONS } from "@agir/donations/spendingRequest/common/form.config";
import { displayPrice } from "@agir/lib/utils/display";
import { simpleDate } from "@agir/lib/utils/time";
import SpendingRequestHistory from "../SpendingRequestHistory";

const FlexLine = styled.div`
  display: flex;
  flex-flow: row wrap;
  gap: 1rem;

  & > * {
    flex: 1 1 auto;
  }

  h4& {
    span + span {
      flex: 0 0 auto;
    }
  }
`;

const StyledCard = styled(Card).attrs(() => ({
  bordered: false,
}))`
  display: flex;
  flex-flow: column nowrap;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 400;
  padding: 1.375rem;
  box-shadow: none;
  border-bottom: 1px solid ${(props) => props.theme.black100};
  margin-bottom: 0;

  header {
    display: flex;
    flex-flow: row nowrap;
    gap: 1rem;
  }

  h3,
  h4,
  p {
    flex: 1 1 auto;
    font-size: inherit;
    margin: 0;
  }

  h3 {
    font-size: 1.125rem;
    line-height: 2;
    font-weight: 700;
  }

  h4 {
    font-weight: 700;
  }

  p + h4 {
    margin-top: 0.5rem;
  }

  p > strong {
    font-weight: 600;
  }

  em {
    font-size: 0.875rem;
    font-weight: 400;
  }
`;

const SpendingRequestDetails = (props) => {
  const {
    spendingRequest,
    onAttachmentAdd,
    onAttachmentChange,
    onAttachmentDelete,
  } = props;

  const { timing, spendingDate, amount } = spendingRequest;

  const spendingRequestTiming = useMemo(
    () => (timing && TIMING_OPTIONS[timing]?.shortLabel) || "",
    [timing]
  );
  const spendingRequestSpendingDate = useMemo(
    () => (spendingDate ? simpleDate(spendingDate, false) : ""),
    [spendingDate]
  );
  const spendingRequestAmount = useMemo(
    () => (amount ? displayPrice(amount, true) : "— €"),
    [amount]
  );

  return (
    <div>
      <StyledCard>
        <SpendingRequestHistory status={spendingRequest.status} />
        <Button
          link
          route="spendingRequestHistory"
          routeParams={{ spendingRequestPk: spendingRequest.id }}
          icon="arrow-right"
          color="choose"
        >
          Voir le suivi
        </Button>
      </StyledCard>
      <StyledCard>
        <header>
          <h3>Détails</h3>
        </header>
        <h4>{spendingRequest.title}</h4>
        <p>Dépense {spendingRequestTiming.toLowerCase()}</p>

        <h4>Motif de l'achat</h4>
        <p>{spendingRequest.explanation || <em>Non renseigné</em>}</p>

        <h4>Catégorie de dépense</h4>
        <p>
          <CategoryCard small category={spendingRequest.category} />
        </p>

        <h4>Date de l'achat</h4>
        <p>{spendingRequestSpendingDate || <em>Non renseignée</em>}</p>

        <h4>Événement lié à la dépense</h4>
        <p>{spendingRequest.event?.name || <em>Pas d'évenement</em>}</p>

        <h4>Mode de paiement</h4>
        <p>{spendingRequest.contact?.name || <em>Non renseigné</em>}</p>

        <h4>Numéro de téléphone</h4>
        <p>{spendingRequest.contact?.phone || <em>Non renseigné</em>}</p>
      </StyledCard>
      <StyledCard>
        <header>
          <h3>Montant et financement</h3>
        </header>
        <Spacer size="0" />
        <FlexLine as="h4">
          <span>Total de la dépense</span>
          <span>{spendingRequestAmount}</span>
        </FlexLine>
        <p style={{ fontSize: "0.875rem" }}>
          Payé par le groupe&nbsp;:{" "}
          <strong>{spendingRequest.group.name}</strong>
        </p>
      </StyledCard>
      <StyledCard>
        <header>
          <h3>Paiement</h3>
        </header>

        <h4>Mode de paiement</h4>
        <p>Virement</p>

        <h4>Titulaire du compte</h4>
        <p>{spendingRequest.bankAccount?.name || <em>Non renseigné</em>}</p>

        <h4>IBAN</h4>
        <p>{spendingRequest.bankAccount?.iban || <em>Non renseigné</em>}</p>

        <h4>BIC</h4>
        <p>{spendingRequest.bankAccount?.bic || <em>Non renseigné</em>}</p>

        <h4>RIB</h4>
        <p>
          {spendingRequest.bankAccount?.rib ? (
            <AttachmentItem
              id={spendingRequest.bankAccount.rib}
              type="RIB"
              title="Relevé d'Identité Bancare"
              file={spendingRequest.bankAccount.rib}
            />
          ) : (
            <em>
              &mdash;&nbsp;Pour la validation de la demande, vous devrez
              également joindre le{" "}
              <abbr title="Relevé d'Identité Bancaire">RIB</abbr> du compte
              bancaire au format PDF, JPEG ou PNG.
            </em>
          )}
        </p>
      </StyledCard>
      <StyledCard>
        <header>
          <h3>Pièces justificatives</h3>
          <Button small icon="plus" onClick={onAttachmentAdd}>
            Ajouter
          </Button>
        </header>
        {Array.isArray(spendingRequest.attachments) &&
        spendingRequest.attachments.length > 0 ? (
          <AttachmentList
            attachments={spendingRequest.attachments}
            onEdit={onAttachmentChange}
            onDelete={onAttachmentDelete}
          />
        ) : (
          <em>
            &mdash;&nbsp;Aucune pièce justificative n'a pas encore été ajoutée
          </em>
        )}
      </StyledCard>
    </div>
  );
};

SpendingRequestDetails.propTypes = {
  spendingRequest: PropTypes.object,
  onAttachmentAdd: PropTypes.func,
  onAttachmentChange: PropTypes.func,
  onAttachmentDelete: PropTypes.func,
};

export default SpendingRequestDetails;
