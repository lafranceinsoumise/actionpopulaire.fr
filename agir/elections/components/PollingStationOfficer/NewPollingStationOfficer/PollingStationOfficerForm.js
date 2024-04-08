import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";

import Spacer from "@agir/front/genericComponents/Spacer";
import Steps, { useSteps } from "@agir/front/genericComponents/Steps";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import CountryField from "@agir/front/formComponents/CountryField";
import DateTimeField from "@agir/front/formComponents/DateTimeField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import RadioField from "@agir/front/formComponents/RadioField";
import TextField from "@agir/front/formComponents/TextField";

import CirconscriptionLegislativeField from "@agir/elections/Common/CirconscriptionLegislativeField";
import PollingStationField from "@agir/elections/Common/PollingStationField";
import VotingLocationField from "@agir/elections/Common/VotingLocationField";
import VotingDateFields from "@agir/elections/Common/VotingDateFields";

import NewPollingStationOfficerHowTo from "./NewPollingStationOfficerHowTo";
import NewPollingStationOfficerSuccess from "./NewPollingStationOfficerSuccess";

import {
  createPollingStationOfficerOptions,
  createPollingStationOfficer,
  getCirconscriptionsLegislatives,
} from "@agir/elections/Common/api";
import { getInitialData, validatePollingStationOfficer } from "./form.config";

import { getISELink } from "@agir/elections/Common/utils";

const FORM_STEPS = [
  [], // How-to
  [
    "firstName",
    "lastName",
    "birthName",
    "gender",
    "birthDate",
    "birthCity",
    "birthCountry",
  ],
  ["address1", "address2", "zip", "city", "country"],
  [
    ["votingLocation", "votingCommune", "votingConsulate"],
    "pollingStation",
    "voterId",
    "votingCirconscriptionLegislative",
  ],
  ["role", "hasMobility", "availableVotingDates"],
  ["phone", "email", "remarks"],
];

export const getFieldStepFromErrors = (errors) =>
  FORM_STEPS.findIndex(
    (stepFields) =>
      stepFields.length > 0 &&
      stepFields.some((field) =>
        Array.isArray(field)
          ? field.some((subfield) => typeof errors[subfield] !== "undefined")
          : typeof errors[field] !== "undefined",
      ),
  );

const PollingStationOfficerForm = (props) => {
  const { user, initialData } = props;
  const defaults = getInitialData(initialData, user);

  const [formStep, goToPreviousFormStep, goToNextFormStep, setFormStep] =
    useSteps(0);
  const [newPollingStationOfficer, setNewPollingStationOfficer] =
    useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [options, setOptions] = useState({});
  const [data, setData] = useState(defaults);
  const [hasDataAgreement, setHasDataAgreement] = useState(false);
  const [errors, setErrors] = useState(null);

  const isAbroad = data.votingLocation?.type === "consulate";

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

  const handleChangeGender = useCallback((gender) => {
    setErrors((state) => ({
      ...state,
      gender: undefined,
    }));
    setData((state) => ({
      ...state,
      gender,
    }));
  });

  const handleChangeBirthDate = useCallback((birthDate) => {
    setErrors((state) => ({
      ...state,
      birthDate: undefined,
    }));
    setData((state) => ({
      ...state,
      birthDate: birthDate && birthDate.slice(0, 10),
    }));
  }, []);

  const handleChangeBirthCountry = useCallback((birthCountry) => {
    setErrors((state) => ({
      ...state,
      birthCountry: undefined,
    }));
    setData((state) => ({
      ...state,
      birthCountry,
    }));
  }, []);

  const handleChangeCountry = useCallback((country) => {
    setErrors((state) => ({
      ...state,
      country: undefined,
    }));
    setData((state) => ({
      ...state,
      country,
    }));
  }, []);

  const handleSelectVotingLocation = useCallback((votingLocation) => {
    setErrors((state) => ({
      ...state,
      votingLocation: undefined,
      votingCirconscriptionLegislative: undefined,
    }));
    setData((state) => ({
      ...state,
      votingLocation,
      votingCirconscriptionLegislative:
        votingLocation &&
        state.votingLocation &&
        state.votingCirconscriptionLegislative &&
        votingLocation.departement !== state.votingLocation.departement
          ? null
          : state.votingCirconscriptionLegislative,
    }));
  }, []);

  const handleSelectVotingCirconscriptionLegislative = useCallback(
    (votingCirconscriptionLegislative) => {
      setErrors((state) => ({
        ...state,
        votingCirconscriptionLegislative: undefined,
      }));
      setData((state) => ({
        ...state,
        votingCirconscriptionLegislative,
      }));
    },
    [],
  );

  const handleChangeRole = useCallback((role) => {
    setErrors((state) => ({
      ...state,
      role: undefined,
    }));
    setData((state) => ({
      ...state,
      role,
    }));
  }, []);

  const handleChangeHasMobility = useCallback((e) => {
    setErrors((state) => ({
      ...state,
      hasMobility: undefined,
    }));
    setData((state) => ({
      ...state,
      hasMobility: e.target.checked,
    }));
  }, []);

  const handleChangeAvailableVotingDates = useCallback(
    (availableVotingDates) => {
      setErrors((state) => ({
        ...state,
        availableVotingDates: undefined,
      }));
      setData((state) => ({
        ...state,
        availableVotingDates,
      }));
    },
    [],
  );

  const handleChangeDataAgreement = (e) => {
    setHasDataAgreement(e.target.checked);
  };

  const handleErrors = (errors) => {
    setErrors(errors);
    const fieldStep = getFieldStepFromErrors(errors, isAbroad);
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
    const validationErrors = validatePollingStationOfficer(data);
    if (validationErrors) {
      return handleErrors(validationErrors);
    }
    setErrors(null);
    setIsLoading(true);
    const response = await createPollingStationOfficer(data);
    setIsLoading(false);
    if (response.error) {
      return handleErrors(response.error);
    }
    setNewPollingStationOfficer(response.data);
  };

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      const createOptions = await createPollingStationOfficerOptions();
      setIsLoading(false);
      if (createOptions.error || !createOptions.data) {
        setErrors({
          detail: createOptions.error || "Une erreur est survenue.",
        });
        return;
      }
      const votingCirconscriptionLegislative =
        await getCirconscriptionsLegislatives();
      if (
        votingCirconscriptionLegislative.error ||
        !votingCirconscriptionLegislative.data
      ) {
        setErrors({
          detail:
            votingCirconscriptionLegislative.error ||
            "Une erreur est survenue.",
        });
        return;
      }
      const options = {
        gender: createOptions.data.gender.choices.map((choice) => ({
          value: choice.value,
          label: choice.display_name,
        })),
        role: createOptions.data.role.choices.map((choice) => ({
          value: choice.value,
          label: choice.display_name,
        })),
        availableVotingDates:
          createOptions.data.availableVotingDates.choices.map((choice) => ({
            value: choice.value,
            label: choice.display_name,
          })),
        votingCirconscriptionLegislative: votingCirconscriptionLegislative.data,
      };
      setOptions(options);
    };
    init();
  }, []);

  if (newPollingStationOfficer) {
    return <NewPollingStationOfficerSuccess />;
  }

  const globalError = errors?.detail || errors?.global;

  return (
    <Steps
      as="form"
      onSubmit={handleSubmit}
      isLoading={isLoading}
      disabled={!hasDataAgreement || isLoading}
      title="devenir assesseur·e ou délégué·e"
      step={formStep}
      goToPrevious={goToPreviousFormStep}
      goToNext={goToNextFormStep}
    >
      <NewPollingStationOfficerHowTo />
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
        <TextField
          disabled={isLoading}
          id="birthName"
          name="birthName"
          value={data.birthName}
          onChange={handleChange}
          error={errors?.birthName}
          label="Nom de naissance (si necessaire)"
          helpText="Indiquer votre nom de naissance si, par exemple, vous vous êtes marié·e"
        />
        <Spacer size="1rem" />
        <RadioField
          required
          disabled={isLoading}
          id="gender"
          name="gender"
          value={data.gender}
          onChange={handleChangeGender}
          error={errors?.gender}
          label="Genre (à l'état civil)"
          options={options?.gender || []}
        />
        <Spacer size="1rem" />
        <DateTimeField
          required
          type="date"
          disabled={isLoading}
          id="birthDate"
          name="birthDate"
          value={data.birthDate}
          onChange={handleChangeBirthDate}
          error={errors?.birthDate}
          label="Date de naissance"
          autoComplete="birthday"
        />
        <Spacer size="1rem" />
        <TextField
          required
          disabled={isLoading}
          id="birthCity"
          name="birthCity"
          value={data.birthCity}
          onChange={handleChange}
          error={errors?.birthCity}
          label="Commune de naissance"
        />
        <Spacer size="1rem" />
        <CountryField
          required
          disabled={isLoading}
          id="birthCountry"
          name="birthCountry"
          value={data.birthCountry}
          onChange={handleChangeBirthCountry}
          error={errors?.birthCountry}
          label="Pays de naissance"
        />
      </fieldset>
      <fieldset>
        <TextField
          autoFocus
          required
          disabled={isLoading}
          id="address1"
          name="address1"
          value={data.address1}
          onChange={handleChange}
          error={errors?.address1}
          label="Adresse"
          autoComplete="address-line1"
        />
        <Spacer size="1rem" />
        <TextField
          required
          disabled={isLoading}
          id="address2"
          name="address2"
          value={data.address2}
          onChange={handleChange}
          error={errors?.address2}
          label="Complément d'adresse (facultatif)"
          autoComplete="address-line2"
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
          label="Code postal"
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
          label="Commune"
          autoComplete="locality"
        />
        <Spacer size="1rem" />
        <CountryField
          required
          disabled={isLoading}
          id="country"
          name="country"
          value={data.country}
          onChange={handleChangeCountry}
          error={errors?.country}
          label="Pays"
        />
      </fieldset>
      <fieldset>
        <VotingLocationField
          autoFocus
          required
          disabled={isLoading}
          id="votingLocation"
          name="votingLocation"
          value={data.votingLocation}
          onChange={handleSelectVotingLocation}
          error={
            errors?.votingLocation ||
            errors?.votingCommune ||
            errors?.votingConsulate
          }
          label="Commune ou ambassade d'inscription aux listes électorales"
        />
        <Spacer size="1rem" />
        <PollingStationField
          isAbroad={isAbroad}
          countries={data?.votingLocation?.countries}
          disabled={isLoading}
          id="pollingStation"
          name="pollingStation"
          onChange={handleChange}
          value={data.pollingStation}
          error={errors?.pollingStation}
          label="Bureau de vote"
          helpText={
            <span>
              Vous pouvez vérifier votre bureau de vote sur votre carte
              éléctorale ou sur{" "}
              <a
                href={getISELink(data)}
                target="_blank"
                rel="noopener noreferrer"
              >
                le site du service public
              </a>
            </span>
          }
        />
        <Spacer size="1rem" />
        <TextField
          disabled={isLoading}
          id="voterId"
          name="voterId"
          onChange={handleChange}
          value={data.voterId}
          error={errors?.voterId}
          label="Numéro national d'électeur"
          helpText={
            <span>
              Vous pouvez retrouver votre numéro national d'électeur sur votre
              carte éléctorale ou sur{" "}
              <a
                href={getISELink(data)}
                target="_blank"
                rel="noopener noreferrer"
              >
                le site du service public
              </a>
            </span>
          }
        />
        <Spacer size="1rem" />
        <CirconscriptionLegislativeField
          disabled={isLoading}
          id="votingCirconscriptionLegislative"
          name="votingCirconscriptionLegislative"
          onChange={handleSelectVotingCirconscriptionLegislative}
          value={data.votingCirconscriptionLegislative}
          error={errors?.votingCirconscriptionLegislative}
          label="Circonscription législative d'inscription"
          options={options?.votingCirconscriptionLegislative}
          votingLocation={data?.votingLocation}
        />
      </fieldset>
      <fieldset>
        <RadioField
          autoFocus
          required
          disabled={isLoading}
          id="role"
          name="role"
          value={data.role}
          onChange={handleChangeRole}
          error={errors?.role}
          label="Rôle"
          placeholder="Choisir un rôle"
          options={options?.role || []}
        />
        <Spacer size="1rem" />
        <VotingDateFields
          required
          disabled={isLoading}
          id="availableVotingDates"
          name="availableVotingDates"
          value={data.availableVotingDates}
          onChange={handleChangeAvailableVotingDates}
          error={errors?.availableVotingDates}
          label="Dates de disponibilité (obligatoire)"
          labelSingle="Date du scrutin :"
          options={options?.availableVotingDates || []}
        />
        <Spacer size="1rem" />
        <p style={{ fontWeight: 600 }}>Mobilité</p>
        <Spacer size=".5rem" />
        <CheckboxField
          disabled={isLoading}
          id="hasMobility"
          name="hasMobility"
          value={!!data?.hasMobility}
          onChange={handleChangeHasMobility}
          error={errors?.hasMobility}
          label="Je suis disponible à tenir un autre bureau de vote que celui dans lequel je suis inscrit·e, si nécessaire"
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
          label="Téléphone mobile"
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
          rows={2}
          hasCounter={!!data.remarks}
          maxLength={255}
          disabled={isLoading}
          id="remarks"
          name="remarks"
          value={data.remarks}
          onChange={handleChange}
          error={errors?.remarks}
          label="Remarques ou question (facultatif)"
          helpText="Quand êtes-vous disponible pour être contacté·e, en semaine et le week-end ?"
        />
        <Spacer size="1rem" />
        <CheckboxField
          disabled={isLoading}
          id="dataAgreement"
          name="dataAgreement"
          value={hasDataAgreement}
          onChange={handleChangeDataAgreement}
          label={
            <>
              J'autorise Action Populaire à partager mes coordonnées pour être
              mis·e en contact avec les équipes de campagne de la{" "}
              <abbr title="Nouvelle Union Populaire Écologique et Sociale">
                NUPES
              </abbr>{" "}
              près de chez moi, dans le cadre de la désignation des assesseur·es
              et délégué·es de bureau de vote
            </>
          }
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
  );
};

PollingStationOfficerForm.propTypes = {
  user: PropTypes.oneOfType([PropTypes.object, PropTypes.bool]),
};

export default PollingStationOfficerForm;
