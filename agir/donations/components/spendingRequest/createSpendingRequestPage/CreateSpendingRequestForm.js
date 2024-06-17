import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";
import AmountField from "@agir/donations/spendingRequest/common/AmountField";
import AttachmentWidget from "@agir/donations/spendingRequest/common/AttachmentWidget";
import BankAccountField from "@agir/donations/spendingRequest/common/BankAccountField";
import CategoryField from "@agir/donations/spendingRequest/common/CategoryField";
import ContactField from "@agir/donations/spendingRequest/common/ContactField";
import EventField from "@agir/donations/spendingRequest/common/EventField";
import AgreementField from "@agir/donations/spendingRequest/common/SpendingRequestAgreement";
import AppRedirect from "@agir/front/app/Redirect";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import DateTimeField from "@agir/front/formComponents/DateTimeField";
import RadioField from "@agir/front/formComponents/RadioField";
import TextField from "@agir/front/formComponents/TextField";
import Spacer from "@agir/front/genericComponents/Spacer";
import Steps, { useSteps } from "@agir/front/genericComponents/Steps";
import { Hide } from "@agir/front/genericComponents/grid";

import { createSpendingRequest } from "@agir/donations/spendingRequest/common/api";
import {
  TIMING_OPTIONS,
  getInitialData,
  validateSpendingRequest,
} from "@agir/donations/spendingRequest/common/form.config";

const FORM_STEP_NAMES = [
  "Détails",
  "Pièces justificatives",
  "Montant et financement",
  "Coordonnées bancaires",
  "Finalisation",
];

const FORM_STEPS = [
  [
    "timing",
    "title",
    "campaign",
    "category",
    "explanation",
    "event",
    "spendingDate",
    "contact",
  ],
  ["attachments"],
  ["amount"],
  ["bankAccount"],
  ["agreement", "global"],
];

const timingOptions = Object.values(TIMING_OPTIONS);

const StyledLabel = styled.h6`
  font-size: 1.375rem;
  font-weight: 700;
  margin: 0 0 1.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    font-size: 1.125rem;
    margin: 0 0 1rem;
  }
`;

const StyledGlobalError = styled.p`
  padding: 1rem 0 0;
  margin: 0;
  font-size: 1rem;
  color: ${(props) => props.theme.redNSP};
`;

const StyledFieldset = styled.fieldset`
  padding: 2rem;
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 0;
    box-shadow: none;
    border-radius: 0;
  }
`;

export const getFieldStepFromErrors = (errors) =>
  FORM_STEPS.findIndex(
    (stepFields) =>
      stepFields.length > 0 &&
      stepFields.some((field) => typeof errors[field] !== "undefined"),
  );

const CreateSpendingRequestForm = (props) => {
  const { user, group, availableAmount = 0 } = props;
  const [formStep, goToPreviousFormStep, goToNextFormStep, goToStep] =
    useSteps(0);
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState(getInitialData(user, group));
  const [errors, setErrors] = useState(null);
  const [hasAgreement, setHasAgreement] = useState();

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setErrors((state) => ({
      ...state,
      [name]: undefined,
    }));
    setData((state) => ({
      ...state,
      [name]: value,
    }));
  }, []);

  const handleChangeNested = useCallback((name, prop, value) => {
    setErrors((state) => ({
      ...state,
      [name]: {
        ...((state && state[name]) || {}),
        [prop]: undefined,
      },
    }));
    setData((state) => ({
      ...state,
      [name]: {
        ...((state && state[name]) || {}),
        [prop]: value,
      },
    }));
  }, []);

  const handleChangeCampaign = useCallback((e) => {
    const { name, checked } = e.target;
    setErrors((state) => ({
      ...state,
      [name]: undefined,
    }));
    setData((state) => ({
      ...state,
      [name]: checked,
    }));
  }, []);

  const handleChangeTiming = useCallback((value) => {
    setErrors((state) => ({
      ...state,
      timing: undefined,
    }));
    setData((state) => ({
      ...state,
      timing: value,
    }));
  }, []);

  const handleChangeCategory = useCallback((value) => {
    setErrors((state) => ({
      ...state,
      category: undefined,
    }));
    setData((state) => ({
      ...state,
      category: value,
    }));
  }, []);

  const handleChangeEvent = useCallback((value) => {
    setErrors((state) => ({
      ...state,
      event: undefined,
    }));
    setData((state) => ({
      ...state,
      event: value,
    }));
  }, []);

  const handleChangeSpendingDate = useCallback((value) => {
    setErrors((state) => ({
      ...state,
      spendingDate: undefined,
    }));
    setData((state) => ({
      ...state,
      spendingDate: value ? value.split("T")[0] : value,
    }));
  }, []);

  const handleChangeAttachments = useCallback((value, dismissErrorIndex) => {
    if (typeof dismissErrorIndex === "number") {
      setErrors((state) => ({
        ...state,
        attachments: Array.isArray(state.attachments)
          ? [
              ...state.attachments.slice(0, dismissErrorIndex),
              ...state.attachments.slice(dismissErrorIndex + 1),
            ]
          : state.attachments,
      }));
    }
    setData((state) => ({
      ...state,
      attachments: value,
    }));
  }, []);

  const handleChangeAmount = useCallback((value) => {
    setErrors((state) => ({
      ...state,
      amount: undefined,
    }));
    setData((state) => ({
      ...state,
      amount: value,
    }));
  }, []);

  const handleErrors = useCallback(
    (errors) => {
      errors = typeof errors === "string" ? { global: errors } : errors;
      setErrors(errors);
      const fieldStep = getFieldStepFromErrors(errors);
      if (
        typeof fieldStep === "number" &&
        fieldStep >= 0 &&
        fieldStep !== formStep
      ) {
        goToStep(fieldStep);
      }
    },
    [formStep, goToStep],
  );

  const saveRequest = useCallback(
    async (shouldValidate = false) => {
      const validationErrors = validateSpendingRequest(data, shouldValidate);
      if (validationErrors) {
        return handleErrors(validationErrors);
      }
      setErrors(null);
      setIsLoading(true);
      const response = await createSpendingRequest(data, shouldValidate);
      if (response.error) {
        handleErrors(response.error);
      } else {
        setData({ ...data, id: response.data.id });
      }
      setIsLoading(false);
    },
    [data, handleErrors],
  );

  const handleSave = useCallback(
    async (e) => {
      e.preventDefault();
      saveRequest(false);
    },
    [saveRequest],
  );

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      saveRequest(true);
    },
    [saveRequest],
  );

  const globalError = errors?.global || errors?.detail;

  if (data.id) {
    return (
      <AppRedirect
        route="spendingRequestDetails"
        routeParams={{ spendingRequestPk: data.id }}
        toast="La demande a bien été enregistrée"
      />
    );
  }

  return (
    <Steps
      as="form"
      type="index"
      stepNames={FORM_STEP_NAMES}
      onSave={handleSave}
      onSubmit={handleSubmit}
      isLoading={isLoading}
      disabled={!hasAgreement}
      step={formStep}
      goToPrevious={goToPreviousFormStep}
      goToNext={goToNextFormStep}
      goToStep={goToStep}
    >
      <StyledFieldset style={{ margin: 0 }}>
        <Hide
          $over
          style={{
            textAlign: "right",
            marginBottom: "1.5rem",
            fontSize: "0.875rem",
          }}
        >
          <Button
            link
            small
            color="link"
            icon="arrow-right"
            route="spendingRequestHelp"
          >
            Un doute ? Consultez le centre d'aide
          </Button>
        </Hide>
        <Hide $under as={StyledLabel}>
          Détails (obligatoire)
        </Hide>
        <CheckboxField
          toggle
          autoFocus
          disabled={isLoading}
          id="campaign"
          name="campaign"
          value={data.campaign}
          onChange={handleChangeCampaign}
          label="Il s’agit d’une dépense effectuée dans le cadre de la campagne pour les élections européennes 2024"
        />
        <hr />
        <RadioField
          disabled={isLoading}
          id="timing"
          name="timing"
          value={data.timing}
          onChange={handleChangeTiming}
          label=""
          options={timingOptions}
        />
        <Spacer size="2rem" />
        <TextField
          disabled={isLoading}
          id="title"
          name="title"
          value={data.title}
          onChange={handleChange}
          error={errors?.title}
          label="Titre de la dépense (obligatoire)"
          maxLength={200}
          hasCounter={false}
        />
        <Spacer size="2rem" />
        <StyledLabel>Catégorie de dépense (obligatoire)</StyledLabel>
        <CategoryField
          disabled={isLoading}
          id="category"
          name="category"
          value={data.category}
          onChange={handleChangeCategory}
          error={errors?.category}
          label=""
        />
        <Spacer size="1.5rem" />
        <TextField
          disabled={isLoading}
          id="explanation"
          name="explanation"
          value={data.explanation}
          onChange={handleChange}
          error={errors?.explanation}
          label="Motif de l'achat (obligatoire)"
          textArea
          rows={3}
          maxLength={1500}
          hasCounter
        />
        <Spacer size="1.5rem" />
        <EventField
          disabled={isLoading}
          groupPk={group?.id}
          id="event"
          name="event"
          value={data.event}
          onChange={handleChangeEvent}
          error={errors?.event}
          label="Événement lié à la dépense"
        />
        <Spacer size="1.5rem" />
        <DateTimeField
          type="date"
          disabled={isLoading}
          id="spendingDate"
          name="spendingDate"
          value={data.spendingDate}
          onChange={handleChangeSpendingDate}
          error={errors?.spendingDate}
          label="Date de l'achat (obligatoire)"
        />
        <Spacer size="1.5rem" />
        <ContactField
          id="contact"
          name="contact"
          disabled={isLoading}
          value={data.contact}
          onChange={handleChangeNested}
          error={errors?.contact}
        />
      </StyledFieldset>
      <StyledFieldset>
        <Hide $under as={StyledLabel}>
          Pièces justificatives (obligatoire)
        </Hide>
        <AttachmentWidget
          id="attachments"
          name="attachments"
          disabled={isLoading}
          value={data.attachments}
          onChange={handleChangeAttachments}
          error={errors?.attachments}
        />
      </StyledFieldset>
      <StyledFieldset>
        <Hide $under as={StyledLabel}>
          Montant et financement (obligatoire)
        </Hide>
        <AmountField
          value={data.amount}
          onChange={handleChangeAmount}
          error={errors?.amount}
          disabled={isLoading}
          availableAmount={availableAmount}
        />
      </StyledFieldset>
      <StyledFieldset>
        <Hide $under as={StyledLabel}>
          Coordonnées bancaires (obligatoire)
        </Hide>
        <BankAccountField
          id="bankAccount"
          name="bankAccount"
          value={data.bankAccount}
          onChange={handleChangeNested}
          error={errors?.bankAccount}
        />
      </StyledFieldset>
      <StyledFieldset>
        <StyledLabel>Validation (obligatoire)</StyledLabel>
        <AgreementField onChange={setHasAgreement} disabled={isLoading} />
        {globalError && (
          <StyledGlobalError>
            {Array.isArray(globalError) ? globalError[0] : globalError}
          </StyledGlobalError>
        )}
      </StyledFieldset>
    </Steps>
  );
};

CreateSpendingRequestForm.propTypes = {
  user: PropTypes.object,
  group: PropTypes.object,
  availableAmount: PropTypes.number,
};

export default CreateSpendingRequestForm;
