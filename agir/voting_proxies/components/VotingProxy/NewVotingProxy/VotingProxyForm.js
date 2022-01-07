import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import Steps, { useSteps } from "@agir/front/genericComponents/Steps";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import DateTimeField from "@agir/front/formComponents/DateTimeField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import TextField from "@agir/front/formComponents/TextField";
import VotingLocationField from "@agir/voting_proxies/Common/VotingLocationField";
import VotingDateFields from "@agir/voting_proxies/Common/VotingDateFields";

import NewVotingProxyHowTo from "./NewVotingProxyHowTo";
import NewVotingProxySuccess from "./NewVotingProxySuccess";

import {
  createVotingProxyOptions,
  createVotingProxy,
} from "@agir/voting_proxies/Common/api";
import { getInitialData, validateVotingProxy } from "./form.config";

const FORM_STEPS = [
  [], // How-to
  ["votingLocation", "pollingStationNumber", "votingDates"],
  ["firstName", "lastName", "dateOfBirth"],
  ["phone", "email", "remarks"],
];

export const getFieldStepFromErrors = (errors) =>
  FORM_STEPS.findIndex(
    (stepFields) =>
      stepFields.length > 0 &&
      stepFields.some((field) => typeof errors[field] !== "undefined")
  );

const VotingProxyForm = (props) => {
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

  const handleChangeDateOfBirth = useCallback((dateOfBirth) => {
    setErrors((state) => ({
      ...state,
      dateOfBirth: undefined,
    }));
    setData((state) => ({
      ...state,
      dateOfBirth: dateOfBirth && dateOfBirth.slice(0, 10),
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
    const validationErrors = validateVotingProxy(data);
    if (validationErrors) {
      return handleErrors(validationErrors);
    }
    setErrors(null);
    setIsLoading(true);
    const response = await createVotingProxy(data);
    setIsLoading(false);
    if (response.error) {
      return handleErrors(response.error);
    }
    setIsCreated(true);
  };

  useEffect(async () => {
    setIsLoading(true);
    const options = await createVotingProxyOptions();
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
    return <NewVotingProxySuccess />;
  }

  return (
    <Steps
      as="form"
      onSubmit={handleSubmit}
      isLoading={isLoading}
      disabled={!hasDataAgreement || isLoading}
      title="voter au nom d'un·ne citoyen·ne"
      step={formStep}
      goToPrevious={goToPreviousFormStep}
      goToNext={goToNextFormStep}
    >
      <NewVotingProxyHowTo />
      <fieldset>
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
        <Spacer size="1rem" />
        <VotingDateFields
          required
          disabled={isLoading}
          id="votingDates"
          name="votingDates"
          value={data.votingDates}
          onChange={handleChangeVotingDates}
          error={errors?.votingDates}
          label="Dates de disponibilité"
          options={votingDateOptions}
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
        <DateTimeField
          required
          type="date"
          disabled={isLoading}
          id="dateOfBirth"
          name="dateOfBirth"
          value={data.dateOfBirth}
          onChange={handleChangeDateOfBirth}
          error={errors?.dateOfBirth}
          label="Date de naissance"
          autoComplete="birthday"
        />
      </fieldset>
      <fieldset>
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
        <TextField
          textArea
          disabled={isLoading}
          id="remarks"
          name="remarks"
          value={data.remarks}
          onChange={handleChange}
          error={errors?.remarks}
          label="Moments de disponibilité en semaine (facultatif)"
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
              padding: 0 0 1rem;
              margin: 0;
              font-size: 1rem;
              text-align: center;
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

export default VotingProxyForm;
