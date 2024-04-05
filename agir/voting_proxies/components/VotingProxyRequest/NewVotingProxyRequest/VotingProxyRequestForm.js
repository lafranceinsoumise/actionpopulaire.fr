import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";

import Spacer from "@agir/front/genericComponents/Spacer";
import Steps, { useSteps } from "@agir/front/genericComponents/Steps";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Link from "@agir/front/app/Link";
import PhoneField from "@agir/front/formComponents/PhoneField";
import TextField from "@agir/front/formComponents/TextField";

import PollingStationField from "@agir/elections/Common/PollingStationField";
import VotingDateFields from "@agir/elections/Common/VotingDateFields";
import VotingLocationField from "@agir/elections/Common/VotingLocationField";
import FormFooter from "@agir/voting_proxies/Common/FormFooter";

import NewVotingProxyRequestHowTo from "./NewVotingProxyRequestHowTo";
import NewVotingProxyRequestIntro from "./NewVotingProxyRequestIntro";
import NewVotingProxyRequestSuccess from "./NewVotingProxyRequestSuccess";

import {
  createVotingProxyRequest,
  createVotingProxyRequestOptions,
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
      stepFields.some((field) => typeof errors[field] !== "undefined"),
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

  const handleChangePollingStation = useCallback((e) => {
    const { name, value } = e.target;
    if (value) {
      setErrors((state) => ({
        ...state,
        [name]: undefined,
      }));
    }
    setData((state) => ({
      ...state,
      [name]: value,
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
    if (
      typeof fieldStep === "number" &&
      fieldStep >= 0 &&
      fieldStep !== formStep
    ) {
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

  useEffect(() => {
    const effect = async () => {
      setIsLoading(true);
      const options = await createVotingProxyRequestOptions();
      setIsLoading(false);
      if (options.error || !options.data?.votingDates) {
        setErrors({ detail: options.error || "Une erreur est survenue." });
      } else {
        setVotingDateOptions(
          options.data.votingDates.choices.map((choice) => ({
            value: choice.value,
            label: choice.display_name,
          })),
        );
      }
    };
    effect();
  }, []);

  if (isCreated) {
    return (
      <>
        <NewVotingProxyRequestSuccess />
        <Spacer size="4rem" />
        <FormFooter />
      </>
    );
  }

  const globalError = errors?.global || errors?.detail;

  return (
    <>
      <Steps
        as="form"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        disabled={!hasDataAgreement || isLoading}
        title="Faire une procuration pour que quelqu'un vote à ma place"
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
            error={
              errors?.votingLocation || errors?.commune || errors?.consulate
            }
            label="Commune ou ambassade d'inscription aux listes électorales"
          />
          <Spacer size="1rem" />
          <PollingStationField
            isAbroad={data.votingLocation?.type === "consulate"}
            countries={data?.votingLocation?.countries}
            disabled={isLoading}
            id="pollingStationNumber"
            name="pollingStationNumber"
            value={data.pollingStationNumber}
            onChange={handleChangePollingStation}
            error={errors?.pollingStationNumber}
            label="Votre bureau de vote"
            helpText={
              <>
                Vous pouvez vérifier votre bureau de vote sur votre carte
                électorale ou sur{" "}
                <Link
                  href="https://www.service-public.fr/particuliers/vosdroits/services-en-ligne-et-formulaires/ISE"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  le site du service public
                </Link>
                .
              </>
            }
          />
        </fieldset>
        <fieldset>
          <TextField
            autoFocus
            required
            disabled={isLoading}
            id="firstName"
            name="firstName"
            value={data.firstName}
            onChange={handleChange}
            error={errors?.firstName}
            label="Vos prénoms"
            helpText="Tous vos prénoms tels qu'ils apparaissent sur votre pièce d'identité"
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
            label="Votre nom de famille"
            helpText="Tel qu'il apparaît sur votre pièce d'identité"
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
            label="Votre numéro de téléphone mobile"
            helpText="Vous recevrez un SMS pour la mise en relation avec la personne qui prendra votre procuration"
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
            label="Votre adresse e-mail"
            helpText="Important : si vous vous êtes déjà inscrit·e sur lafranceinsoumise.fr ou actionpopulaire.fr, utilisez la même adresse e-mail."
            autoComplete="email"
          />
          <Spacer size="1rem" />
          <CheckboxField
            disabled={isLoading}
            id="dataAgreement"
            name="dataAgreement"
            value={hasDataAgreement}
            onChange={handleChangeDataAgreement}
            label="J’autorise la France insoumise à partager mes coordonnées pour être mis·e en contact dans le cadre d’une procuration"
          />
          {globalError && (
            <p
              css={`
                padding: 1rem 0 0;
                margin: 0;
                font-size: 1rem;
                color: ${({ theme }) => theme.redNSP};
              `}
            >
              {Array.isArray(globalError) ? globalError[0] : globalError}
            </p>
          )}
        </fieldset>
      </Steps>
      <Spacer size="0.5rem" />
      <FormFooter votingProxyLink={formStep === 0} />
    </>
  );
};

VotingProxyRequestForm.propTypes = {
  user: PropTypes.object,
};

export default VotingProxyRequestForm;
