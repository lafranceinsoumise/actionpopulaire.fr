import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";
import AttachmentList, {
  AttachmentItem,
} from "@agir/donations/spendingRequest/common/AttachmentList";
import CategoryCard from "@agir/donations/spendingRequest/common/CategoryCard";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import TextField from "@agir/front/formComponents/TextField";
import Card from "@agir/front/genericComponents/Card";
import Spacer from "@agir/front/genericComponents/Spacer";
import SpendingRequestHistory from "../SpendingRequestHistory";

import { TIMING_OPTIONS } from "@agir/donations/spendingRequest/common/form.config";
import { displayPrice } from "@agir/lib/utils/display";
import { simpleDate } from "@agir/lib/utils/time";

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
  bordered: true,
}))`
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;
  padding: 1.5rem;

  header {
    display: flex;
    flex-flow: row nowrap;
    gap: 1rem;
  }

  h3,
  h4,
  p {
    flex: 1 1 auto;
    margin: 0;
  }

  h3 {
    font-size: 1.375rem;
    font-weight: 700;
  }

  h4 {
    font-size: 1.125rem;
    font-weight: 600;
  }

  p > strong {
    font-weight: 600;
  }

  em {
    font-size: 0.875rem;
    font-weight: 400;
  }
`;

const StyledWrapper = styled.div`
  display: grid;
  grid-template-columns: 1fr 25rem;
  align-items: start;
  gap: 1.5rem;
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
    [timing],
  );
  const spendingRequestSpendingDate = useMemo(
    () => (spendingDate ? simpleDate(spendingDate, false) : ""),
    [spendingDate],
  );
  const spendingRequestAmount = useMemo(
    () => (amount ? displayPrice(amount, true) : "— €"),
    [amount],
  );

  return (
    <StyledWrapper>
      <div>
        <StyledCard>
          <header>
            <h3>Détails</h3>
          </header>
          <TextField
            disabled
            readOnly
            id="title"
            name="title"
            label="Titre de la dépense"
            value={spendingRequest.title}
          />
          <CategoryCard category={spendingRequest.category} />
          <FlexLine>
            <TextField
              disabled
              readOnly
              id="timing"
              name="timing"
              label="Type de dépense"
              value={spendingRequestTiming}
            />
            <TextField
              disabled
              readOnly
              id="spendingDate"
              name="spendingDate"
              value={spendingRequestSpendingDate}
              label="Date de l'achat"
            />
          </FlexLine>
          {spendingRequest.campaign && (
            <CheckboxField
              small
              toggle
              disabled
              readOnly
              id="campaign"
              name="campaign"
              label="Il s’agit d’une dépense effectuée dans le cadre de la campagne pour les élections européennes 2024"
              value={spendingRequest.campaign}
            />
          )}
          <TextField
            disabled
            readOnly
            id="event"
            name="event"
            label="Événement lié à la dépense"
            value={spendingRequest.event?.name || ""}
          />
          <TextField
            disabled
            readOnly
            id="explanation"
            name="explanation"
            value={spendingRequest.explanation}
            label="Motif de l'achat"
            textArea
            rows={1}
          />
          <TextField
            disabled
            readOnly
            id="contactName"
            name="contactName"
            label="Contact lié à la dépense"
            value={spendingRequest.contact?.name}
          />
          <PhoneField
            disabled
            readOnly
            id="contactPhone"
            name="contactPhone"
            label="Numéro de téléphone"
            value={spendingRequest.contact?.phone}
          />
        </StyledCard>
        <Spacer size="2.5rem" />
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
        <Spacer size="2.5rem" />
        <StyledCard>
          <header>
            <h3>Paiement</h3>
          </header>
          <TextField
            disabled
            readOnly
            id="paymentMode"
            name="paymentMode"
            label="Mode de paiement"
            value="Virement"
          />
          <h4>Coordonnées bancaires</h4>
          <TextField
            disabled
            readOnly
            label="Prénom du titulaire du compte"
            id="bankAccountFirstName"
            name="bankAccountFirstName"
            value={spendingRequest.bankAccount?.firstName}
          />
          <TextField
            disabled
            readOnly
            label="Nom du titulaire du compte"
            id="bankAccountLastName"
            name="bankAccountLastName"
            value={spendingRequest.bankAccount?.lastName}
          />
          <TextField
            disabled
            readOnly
            label={<abbr title="International Bank Account Number">IBAN</abbr>}
            id="bankAccountIban"
            name="bankAccountIban"
            value={spendingRequest.bankAccount?.iban}
          />
          <TextField
            disabled
            readOnly
            label={<abbr title="Bank Identifier Code">BIC</abbr>}
            id="bankAccountBic"
            name="bankAccountBic"
            value={spendingRequest.bankAccount?.bic}
          />
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
        </StyledCard>
        <Spacer size="2.5rem" />
        <StyledCard>
          <header>
            <h3>Pièces justificatives</h3>
            <Button icon="plus" onClick={onAttachmentAdd}>
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
      <SpendingRequestHistory
        status={spendingRequest.status}
        history={spendingRequest.history}
      />
    </StyledWrapper>
  );
};

SpendingRequestDetails.propTypes = {
  spendingRequest: PropTypes.object,
  onAttachmentAdd: PropTypes.func,
  onAttachmentChange: PropTypes.func,
  onAttachmentDelete: PropTypes.func,
};

export default SpendingRequestDetails;
