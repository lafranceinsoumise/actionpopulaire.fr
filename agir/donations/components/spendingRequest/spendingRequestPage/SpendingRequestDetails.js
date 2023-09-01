import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";
import AttachmentList from "@agir/donations/spendingRequest/common/AttachmentList";
import CategoryCard from "@agir/donations/spendingRequest/common/CategoryCard";
import FileField from "@agir/front/formComponents/FileField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import TextField from "@agir/front/formComponents/TextField";
import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { displayPrice } from "@agir/lib/utils/display";
import { simpleDate } from "@agir/lib/utils/time";

const StyledStatus = styled(Card).attrs(() => ({
  bordered: true,
}))`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  font-size: 0.875rem;
  font-weight: 400;

  & > span {
    flex: 1 1 auto;
    max-width: 100%;
    min-height: 1px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  ${RawFeatherIcon} {
    flex: 0 0 auto;
    color: ${({ name, theme }) =>
      name === "clock" ? "#ffb734" : theme.black500};
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

    h3,
    h4 {
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

  return (
    <div>
      <StyledStatus>
        <RawFeatherIcon
          name={spendingRequest.editable ? "edit-3" : "clock"}
          width="1.5rem"
          height="1.5rem"
        />
        <span>{spendingRequest.status}</span>
      </StyledStatus>
      <Spacer size="2.5rem" />
      <StyledCard>
        <header>
          <h3>Détails</h3>
        </header>
        <CategoryCard category={spendingRequest.category} />
        <TextField
          disabled
          readOnly
          id="title"
          name="title"
          label="Titre de la dépense"
          value={spendingRequest.title}
        />
        <TextField
          disabled
          readOnly
          id="spendingDate"
          name="spendingDate"
          value={
            spendingRequest.spendingDate
              ? simpleDate(spendingRequest.spendingDate, false)
              : ""
          }
          label="Date de l'achat"
        />
        <TextField
          disabled
          readOnly
          id="explanation"
          name="explanation"
          value={spendingRequest.explanation}
          label="Motif de l'achat"
          textArea
          rows={3}
        />
        <TextField
          disabled
          readOnly
          id="event"
          name="event"
          label="Événement lié à la dépense"
          value={spendingRequest.event?.name || ""}
        />
      </StyledCard>
      <Spacer size="2.5rem" />
      <StyledCard>
        <header>
          <h3>Contact</h3>
        </header>
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
        <TextField
          disabled
          readOnly
          id="amount"
          name="amount"
          label="Montant TTC"
          value={
            spendingRequest.amount
              ? displayPrice(spendingRequest.amount, true)
              : ""
          }
        />
        <TextField
          disabled
          readOnly
          id="group"
          name="group"
          label="Payé par le groupe d'action"
          value={spendingRequest.group.name}
        />
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
          label="Titulaire du compte"
          id="bankAccountName"
          name="bankAccountName"
          value={spendingRequest.bankAccount?.name}
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
        {spendingRequest.bankAccount?.rib && (
          <FileField
            disabled
            readOnly
            label={<abbr title="Relevé d'Identité Bancaire">RIB</abbr>}
            id="bankAccountRib"
            name="bankAccountRib"
            value="Relevé d'Identité Bancaire"
          />
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
  );
};

SpendingRequestDetails.propTypes = {
  spendingRequest: PropTypes.object,
  onAttachmentAdd: PropTypes.func,
  onAttachmentChange: PropTypes.func,
  onAttachmentDelete: PropTypes.func,
};

export default SpendingRequestDetails;
