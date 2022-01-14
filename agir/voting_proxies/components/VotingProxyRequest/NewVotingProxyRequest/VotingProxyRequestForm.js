import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import Steps, { useSteps } from "@agir/front/genericComponents/Steps";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import TextField from "@agir/front/formComponents/TextField";
import VotingLocationField from "@agir/voting_proxies/Common/VotingLocationField";
import VotingDateFields from "@agir/voting_proxies/Common/VotingDateFields";

import NewVotingProxyRequestIntro from "./NewVotingProxyRequestIntro";
import NewVotingProxyRequestHowTo from "./NewVotingProxyRequestHowTo";
import NewVotingProxyRequestSuccess from "./NewVotingProxyRequestSuccess";

import {
  createVotingProxyRequestOptions,
  createVotingProxyRequest,
} from "@agir/voting_proxies/Common/api";
import { getInitialData, validateVotingProxyRequest } from "./form.config";

const FORM_STEPS = [
  [],
  [],
  ["votingLocation", "pollingStationNumber", "votingDates"],
  ["firstName", "lastName", "phone", "email"],
];

export const getFieldStepFromErrors = (errors) =>
  FORM_STEPS.findIndex(
    (stepFields) =>
      stepFields.length > 0 &&
      stepFields.some((field) => typeof errors[field] !== "undefined")
  );

const VotingProxyRequestForm = (props) => {
  const { user } = props;
  const [formStep, goToPreviousFormStep, goToNextFormStep, setFormStep] =
    useSteps(0);
  const [isCreated, setIsCreated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [votingDateOptions, setVotingDateOptions] = useState([]);
  const [data, setData] = useState(getInitialData(user));
  const [hasDataAgreement, setHasDataAgreement] = useState(false);
  const [errors, setErrors] = useState(null);

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

  const handleSelectPollingLocation = useCallback((votingLocation) => {
    setErrors((state) => ({
      ...state,
      votingLocation: undefined,
    }));
    setData((state) => ({
      ...state,
      votingLocation,
    }));
  }, []);

  const handleChangeVotingDates = useCallback((votingDates) => {
    setErrors((state) => ({
      ...state,
      votingDates: undefined,
    }));
    setData((state) => ({
      ...state,
      votingDates,
    }));
  }, []);

  const handleChangeDataAgreement = (e) => {
    setHasDataAgreement(e.target.checked);
  };

  const handleErrors = (errors) => {
    setErrors(errors);
    const fieldStep = getFieldStepFromErrors(errors);
    if (typeof fieldStep === "number" && fieldStep !== formStep) {
      setFormStep(fieldStep);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validateVotingProxyRequest(data);
    if (validationErrors) {
      return handleErrors(validationErrors);
    }
    setErrors(null);
    setIsLoading(true);
    const response = await createVotingProxyRequest(data);
    setIsLoading(false);
    if (response.error) {
      return handleErrors(response.error);
    }
    setIsCreated(true);
  };

  useEffect(async () => {
    setIsLoading(true);
    const options = await createVotingProxyRequestOptions();
    setIsLoading(false);
    if (options.error || !options.data?.votingDates) {
      setErrors({ global: options.error || "Une erreur est survenue." });
    } else {
      setVotingDateOptions(
        options.data.votingDates.choices.map((choice) => ({
          value: choice.value,
          label: choice.display_name,
        }))
      );
    }
  }, []);

  if (isCreated) {
    return <NewVotingProxyRequestSuccess />;
  }

  return (
    <Steps
      as="form"
      onSubmit={handleSubmit}
      isLoading={isLoading}
      disabled={!hasDataAgreement || isLoading}
      title="donner ma procuration"
      step={formStep}
      goToPrevious={goToPreviousFormStep}
      goToNext={goToNextFormStep}
    >
      <NewVotingProxyRequestIntro />
      <NewVotingProxyRequestHowTo />
      <fieldset>
        <VotingDateFields
          required
          disabled={isLoading}
          id="votingDates"
          name="votingDates"
          value={data.votingDates}
          onChange={handleChangeVotingDates}
          error={errors?.votingDates}
          label="Pour quelle(s) date(s) avez-vous besoin de donner procuration ?"
          options={votingDateOptions}
        />
        <Spacer size="1rem" />
        <VotingLocationField
          required
          disabled={isLoading}
          id="votingLocation"
          name="votingLocation"
          value={data.votingLocation}
          onChange={handleSelectPollingLocation}
          error={errors?.votingLocation || errors?.commune || errors?.consulate}
          label="Commune ou ambassade d'inscription aux listes électorales"
        />
        <Spacer size="1rem" />
        <TextField
          required
          disabled={isLoading}
          id="pollingStationNumber"
          name="pollingStationNumber"
          value={data.pollingStationNumber}
          onChange={handleChange}
          error={errors?.pollingStationNumber}
          label="Numéro du bureau de vote"
          helpText={
            <span>
              Vous pouvez vérifier le numéro de votre bureau de vote sur{" "}
              <a
                href="https://www.service-public.fr/particuliers/vosdroits/services-en-ligne-et-formulaires/ISE"
                target="_blank"
                rel="noopener noreferrer"
              >
                le site du service public
              </a>
            </span>
          }
        />
      </fieldset>
      <fieldset>
        <TextField
          required
          disabled={isLoading}
          id="firstName"
          name="firstName"
          value={data.firstName}
          onChange={handleChange}
          error={errors?.firstName}
          label="Prénoms"
          helpText="Tous vos prénoms, tels qu'ils apparaissent sur la carte électorale"
          autoComplete="given-name"
        />
        <Spacer size="1rem" />
        <TextField
          required
          disabled={isLoading}
          id="lastName"
          name="lastName"
          value={data.lastName}
          onChange={handleChange}
          error={errors?.lastName}
          label="Nom de famille"
          helpText="Votre nom de famille, tel qu'il apparaît sur la carte électorale"
          autoComplete="family-name"
        />
        <Spacer size="1rem" />
        <PhoneField
          required
          disabled={isLoading}
          id="phone"
          name="phone"
          type="phone"
          value={data.phone}
          onChange={handleChange}
          error={errors?.phone}
          label="Téléphone mobile"
          helpText="📱Vous recevrez un SMS pour être mis·e en relation avec votre mandant·e"
          autoComplete="tel"
        />
        <Spacer size="1rem" />
        <TextField
          required
          disabled={isLoading}
          id="email"
          name="email"
          type="email"
          value={data.email}
          onChange={handleChange}
          error={errors?.email}
          label="Adresse e-mail"
          helpText="Important : si vous vous êtes déjà inscrit·e sur lafranceinsoumise.fr ou melenchon2022.fr, utilisez la même adresse e-mail."
          autoComplete="email"
        />
        <Spacer size="1rem" />
        <CheckboxField
          disabled={isLoading}
          id="dataAgreement"
          name="dataAgreement"
          value={hasDataAgreement}
          onChange={handleChangeDataAgreement}
          label="J'autorise Mélenchon 2022 à partager mes coordonnées pour être mis·e en contact dans le cadre d'une procuration"
        />
        {errors?.global && (
          <p
            css={`
              padding: 1rem 0 0;
              margin: 0;
              font-size: 1rem;
              color: ${({ theme }) => theme.redNSP};
            `}
          >
            {errors.global}
          </p>
        )}
      </fieldset>
    </Steps>
  );
};

export default VotingProxyRequestForm;
