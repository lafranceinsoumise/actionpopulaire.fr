import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import Spacer from "@agir/front/genericComponents/Spacer";
import Steps, { useSteps } from "@agir/front/genericComponents/Steps";
import PollingStationField from "@agir/elections/Common/PollingStationField";
import {
  ElectoralInfoLink,
  WarningBlock,
} from "@agir/elections/Common/StyledComponents";
import VotingDateFields from "@agir/elections/Common/VotingDateFields";
import VotingLocationField from "@agir/elections/Common/VotingLocationField";
import AppRedirect from "@agir/front/app/Redirect";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import DateTimeField from "@agir/front/formComponents/DateTimeField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import TextField from "@agir/front/formComponents/TextField";
import FormFooter from "@agir/voting_proxies/Common/FormFooter";
import NewVotingProxyHowTo from "./NewVotingProxyHowTo";
import NewVotingProxySuccess from "./NewVotingProxySuccess";

import {
  createVotingProxy,
  createVotingProxyOptions,
} from "@agir/voting_proxies/Common/api";
import { getInitialData, validateVotingProxy } from "./form.config";

const FORM_STEPS = (isAbroad) =>
  [
    [], // How-to
    ["votingLocation", "pollingStationNumber", "votingDates", "voterId"],
    !isAbroad && ["address", "zip", "city"],
    ["firstName", "lastName", "dateOfBirth"],
    ["phone", "email", "remarks", "subscribed"],
  ].filter(Boolean);

export const getFieldStepFromErrors = (errors, isAbroad) =>
  FORM_STEPS(isAbroad).findIndex(
    (stepFields) =>
      stepFields.length > 0 &&
      stepFields.some((field) => typeof errors[field] !== "undefined"),
  );

const VotingProxyForm = (props) => {
  const { user, onSuccess } = props;

  const location = useLocation();

  const [formStep, goToPreviousFormStep, goToNextFormStep, setFormStep] =
    useSteps(0);
  const [isLoading, setIsLoading] = useState(false);
  const [votingDateOptions, setVotingDateOptions] = useState([]);
  const [data, setData] = useState(getInitialData(user));
  const [hasDataAgreement, setHasDataAgreement] = useState(false);
  const [errors, setErrors] = useState(null);
  const [votingProxy, setVotingProxy] = useState();

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

  const handleSelectVotingLocation = useCallback(
    (votingLocation) => {
      setErrors((state) => ({
        ...state,
        votingLocation: undefined,
      }));
      setData((state) => ({
        ...state,
        votingLocation,
        address: getInitialData(user)?.address,
        zip: getInitialData(user)?.zip,
        city: getInitialData(user)?.city,
      }));
    },
    [user],
  );

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

  const handleChangeSubscribed = useCallback((e) => {
    setErrors((state) => ({
      ...state,
      subscribed: undefined,
    }));
    setData((state) => ({
      ...state,
      subscribed: e.target.checked,
    }));
  }, []);

  const handleChangeDataAgreement = (e) => {
    setHasDataAgreement(e.target.checked);
  };

  const handleErrors = (errors) => {
    setErrors(errors);
    const fieldStep = getFieldStepFromErrors(
      errors,
      data.votingLocation?.type === "consulate",
    );
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
    const validationErrors = validateVotingProxy(
      data,
      data.votingLocation?.type === "consulate",
    );
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
    onSuccess(response.data);
    setVotingProxy(response.data);
  };

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      const options = await createVotingProxyOptions();
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
    init();
  }, []);

  if (votingProxy?.id && location.state?.next) {
    return (
      <AppRedirect
        href={location.state?.next}
        params={{ vp: votingProxy.id }}
      />
    );
  }

  if (votingProxy) {
    return (
      <>
        <NewVotingProxySuccess votingProxyPk={votingProxy.id} />
        <Spacer size="4rem" />
        <FormFooter />
      </>
    );
  }

  const globalError = errors?.detail || errors?.global;

  return (
    <>
      <Steps
        as="form"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        disabled={!hasDataAgreement || isLoading}
        title="voter à la place de quelqu'un"
        step={formStep}
        goToPrevious={goToPreviousFormStep}
        goToNext={goToNextFormStep}
      >
        <NewVotingProxyHowTo user={user} />
        <fieldset>
          <VotingLocationField
            required
            disabled={isLoading}
            id="votingLocation"
            name="votingLocation"
            value={data.votingLocation}
            onChange={handleSelectVotingLocation}
            error={
              errors?.votingLocation || errors?.commune || errors?.consulate
            }
            label="Commune ou ambassade d'inscription aux listes électorales (obligatoire)"
          />
          <Spacer size="1rem" />
          <ElectoralInfoLink />
          <Spacer size="1rem" />
          <PollingStationField
            votingLocation={data?.votingLocation}
            disabled={isLoading}
            id="pollingStationNumber"
            name="pollingStationNumber"
            onChange={handleChangePollingStation}
            value={data.pollingStationNumber}
            error={errors?.pollingStationNumber}
            label="Bureau de vote (obligatoire)"
          />
          <Spacer size="1rem" />
          <TextField
            disabled={isLoading}
            id="voterId"
            name="voterId"
            onChange={handleChange}
            value={data.voterId}
            error={errors?.voterId}
            label="Numéro national d'électeur (8 à 9 chiffres, obligatoire)"
            placeholder="Exemple : 776922959"
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
            label="Dates de disponibilité (obligatoire)"
            labelSingle="Date du scrutin :"
            options={votingDateOptions}
          />
        </fieldset>
        {data.votingLocation?.type === "commune" && (
          <fieldset>
            <WarningBlock>
              Indiquez ci-dessous l'adresse{" "}
              <strong>où vous vous trouverez le jour de vote</strong>. Celle-ci
              sera utilisée pour vous proposer les demandes de procuration de
              vote à proximité.
            </WarningBlock>
            <Spacer size="1.5rem" />
            <TextField
              autoFocus
              required
              disabled={isLoading}
              id="address"
              name="address"
              value={data.address}
              onChange={handleChange}
              error={errors?.address}
              label="Votre adresse (obligatoire)"
              autoComplete="address-line1"
            />
            <Spacer size="1rem" />
            <TextField
              required
              disabled={isLoading}
              id="zip"
              name="zip"
              value={data.zip}
              onChange={handleChange}
              error={errors?.zip}
              label="Votre code postal (obligatoire)"
              autoComplete="postal-code"
            />
            <Spacer size="1rem" />
            <TextField
              required
              disabled={isLoading}
              id="city"
              name="city"
              value={data.city}
              onChange={handleChange}
              error={errors?.city}
              label="Votre commune (obligatoire)"
              helpText="Celle où vous vous trouverez le jour du vote, qui peut être différente de celle où vous êtes inscrit·e"
              autoComplete="locality"
            />
          </fieldset>
        )}
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
            label="Vos prénoms (obligatoire)"
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
            label="Votre nom de famille (obligatoire)"
            helpText="Tel qu'il apparaît sur votre pièce d'identité"
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
            label="Votre date de naissance (obligatoire)"
            autoComplete="birthday"
          />
        </fieldset>
        <fieldset>
          <PhoneField
            autoFocus
            required
            disabled={isLoading}
            id="phone"
            name="phone"
            type="phone"
            value={data.phone}
            onChange={handleChange}
            error={errors?.phone}
            label="Votre numéro de téléphone mobile (obligatoire)"
            helpText="Vous recevrez un SMS pour la mise en relation avec la personne qui vous donnera procuration"
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
            label="Votre adresse e-mail (obligatoire)"
            helpText="Important : si vous vous êtes déjà inscrit·e sur lafranceinsoumise.fr ou actionpopulaire.fr, utilisez la même adresse e-mail."
            autoComplete="email"
          />
          <Spacer size="1rem" />
          <TextField
            textArea
            hasCounter={!!data.remarks}
            maxLength={255}
            disabled={isLoading}
            id="remarks"
            name="remarks"
            value={data.remarks}
            onChange={handleChange}
            error={errors?.remarks}
            label="Vos disponibilités (facultatif)"
            helpText="Quand êtes-vous disponible pour être contacté·e, en semaine et le week-end ?"
          />
          <Spacer size="1rem" />
          <CheckboxField
            disabled={isLoading}
            id="subscribed"
            name="subscribed"
            value={data.subscribed}
            onChange={handleChangeSubscribed}
            label="Je souhaite rejoindre la France insoumise et être informé·e des campagnes du mouvement"
          />
          <CheckboxField
            disabled={isLoading}
            id="dataAgreement"
            name="dataAgreement"
            value={hasDataAgreement}
            onChange={handleChangeDataAgreement}
            label="J'autorise la France insoumise à partager mes coordonnées pour être mis·e en contact dans le cadre d'une procuration"
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
              {globalError}
            </p>
          )}
        </fieldset>
      </Steps>
      <Spacer size="0.5rem" />
      <FormFooter votingProxyRequestLink={formStep === 0} />
    </>
  );
};

VotingProxyForm.propTypes = {
  user: PropTypes.oneOfType([PropTypes.object, PropTypes.bool]),
  onSuccess: PropTypes.func.isRequired,
};

export default VotingProxyForm;
