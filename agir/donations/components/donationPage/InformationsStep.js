import React, { useState } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import useSWR from "swr";

import { MANUAL_REVALIDATION_SWR_CONFIG } from "@agir/front/allPages/SWRContext";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import CountryField from "@agir/front/formComponents/CountryField";
import CustomField from "./CustomField";
import Legal from "./Legal";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import SelectField from "@agir/front/formComponents/SelectField";
import Spacer from "@agir/front/genericComponents/Spacer";
import StaticToast from "@agir/front/genericComponents/StaticToast";
import { StepButton } from "./StyledComponents";
import TextField from "@agir/front/formComponents/TextField";

const StyledPostalCodeTextField = styled(TextField)`
  max-width: 160px;
  width: 160px;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    margin-right: 130px;
  }
`;

const GroupedFields = styled.div`
  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex: 0 1 auto;
    display: flex;
    flex-direction: row;
  }

  @media (max-width: 450px) {
    flex-direction: column;
  }

  & > :last-child {
    flex: 1 1 auto;
  }
`;

const StyledCustomField = styled(CustomField)`
  ${({ hidden }) => (hidden ? "display: none" : "")};
`;

const StyledButton = styled.button`
  display: inline-block;
  background: transparent;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 0;
  margin: 0;
  font-size: 0.813rem;
  text-align: left;
  font-weight: 400;
  width: auto;
`;

const FORM_HELP_TEXT = {
  email:
    "Si vous êtes déjà inscrit·e sur lafranceinsoumise.fr ou melenchon2022.fr, utilisez l'adresse avec laquelle vous êtes inscrit·e",
  nationality: "Si double nationalité dont française : indiquez France",
  contactPhone:
    "Nous sommes dans l'obligation de pouvoir vous contacter en cas de demande de vérification par la CNCCFP.",
  consentCertification:
    "Je certifie sur l'honneur être une personne physique et que le réglement de mon don ne provient pas d'une personne morale (association, société, société civile...) mais de mon compte bancaire personnel.*",
};

const GENDER_OPTIONS = [
  { label: "", value: "" },
  { label: "Madame", value: "F" },
  { label: "Monsieur", value: "M" },
];

const InformationsStep = ({
  onSubmit,
  errors,
  setErrors,
  formData,
  setFormData,
  isLoading,
  hidden = false,
  type = "",
}) => {
  const { data: profile } = useSWR(
    "/api/user/profile/",
    MANUAL_REVALIDATION_SWR_CONFIG
  );

  const [hasAddress2, setHasAddress2] = useState(false);
  const hasNewsletter =
    Array.isArray(profile?.newsletters) &&
    profile.newsletters.includes("2022") &&
    profile.newsletters.includes("2022_exceptionnel");

  const displayAddress2 = () => {
    setHasAddress2(true);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setErrors((error) => ({ ...error, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
  };

  const handleChangeGender = (choice) => {
    setFormData((formData) => ({ ...formData, gender: choice.value }));
  };

  const handleChangeCountry = (country) => {
    setFormData((formData) => ({ ...formData, locationCountry: country }));
  };

  const handleChangeNationality = (country) => {
    setFormData((formData) => ({
      ...formData,
      nationality: country,
      frenchResident: country === "FR",
    }));
  };

  const handleCheckboxChange = (e) => {
    setErrors({ ...errors, [e.target.name]: null });
    setFormData((formData) => ({
      ...formData,
      [e.target.name]: e.target.checked,
    }));
  };

  // Submit with paymentMode
  const handleSubmit = (e, value) => {
    setFormData({ ...formData, paymentMode: value }, () => {
      onSubmit(e);
    });
  };

  const checkPaymentMode =
    Array.isArray(formData.allowedPaymentModes) &&
    formData.allowedPaymentModes.filter((value) => value.includes("check"))[0];

  const cardPaymentMode =
    Array.isArray(formData.allowedPaymentModes) &&
    formData.allowedPaymentModes.filter((value) => !value.includes("check"))[0];

  return (
    <form onSubmit={onSubmit}>
      <StyledCustomField
        Component={TextField}
        id="email"
        name="email"
        label="E-mail*"
        onChange={handleChange}
        value={formData.email}
        error={errors?.email}
        helpText={FORM_HELP_TEXT.email}
        hidden={hidden}
      />
      <GroupedFields>
        <CustomField
          Component={SelectField}
          id="gender"
          name="gender"
          label="Civilité*"
          onChange={handleChangeGender}
          value={GENDER_OPTIONS.find(
            (option) => formData.gender === option.value
          )}
          error={errors?.gender}
          helpText={FORM_HELP_TEXT.gender}
          options={GENDER_OPTIONS}
          placeholder=""
          noSpacer
        />
        <Spacer size="1rem" />
        <CustomField
          Component={TextField}
          id="firstName"
          name="firstName"
          label="Prénom*"
          onChange={handleChange}
          value={formData.firstName}
          error={errors?.firstName}
          helpText={FORM_HELP_TEXT.firstName}
          noSpacer
        />
        <Spacer size="1rem" />
        <CustomField
          Component={TextField}
          id="lastName"
          name="lastName"
          label="Nom de famille*"
          onChange={handleChange}
          value={formData.lastName}
          error={errors?.lastName}
          helpText={FORM_HELP_TEXT.lastName}
          noSpacer
        />
      </GroupedFields>
      <Spacer size="1rem" />
      <CustomField
        Component={CountryField}
        label="Nationalité*"
        name="nationality"
        placeholder=""
        value={formData.nationality}
        onChange={handleChangeNationality}
        error={errors?.nationality}
        helpText={FORM_HELP_TEXT.nationality}
      />
      {formData.nationality !== "FR" && (
        <div data-scroll="frenchResident">
          <CheckboxField
            name="frenchResident"
            label="Je certifie être domicilié⋅e fiscalement en France*"
            value={formData.frenchResident}
            onChange={handleCheckboxChange}
          />
          {errors?.frenchResident && (
            <StaticToast style={{ marginTop: "0.5rem" }}>
              {errors?.frenchResident}
            </StaticToast>
          )}
          <Spacer size="0.5rem" />
        </div>
      )}
      <CustomField
        Component={TextField}
        label="Adresse*"
        name="locationAddress1"
        value={formData.locationAddress1}
        onChange={handleChange}
        error={errors?.locationAddress1}
        helpText={FORM_HELP_TEXT.locationAddress1}
        noSpacer
      />
      {hasAddress2 || formData.locationAddress2 || errors.locationAddress2 ? (
        <>
          <Spacer size="0.5rem" />
          <CustomField
            Component={TextField}
            label=""
            name="locationAddress2"
            value={formData.locationAddress2}
            onChange={handleChange}
            error={errors?.locationAddress2}
            helpText={FORM_HELP_TEXT.locationAddress2}
          />
        </>
      ) : (
        <CustomField
          Component={StyledButton}
          onClick={displayAddress2}
          type="button"
        >
          + Ajouter une deuxième ligne pour l'adresse
        </CustomField>
      )}
      <GroupedFields>
        <CustomField
          Component={StyledPostalCodeTextField}
          label="Code postal*"
          name="locationZip"
          value={formData.locationZip}
          onChange={handleChange}
          error={errors?.locationZip}
          helpText={FORM_HELP_TEXT.locationZip}
          noSpacer
        />
        <Spacer size="1rem" />
        <CustomField
          Component={TextField}
          label="Ville*"
          name="locationCity"
          value={formData.locationCity}
          onChange={handleChange}
          error={errors?.locationCity}
          helpText={FORM_HELP_TEXT.locationCity}
          noSpacer
          style={{ width: "100%" }}
        />
      </GroupedFields>
      <Spacer size="1rem" />
      <CustomField
        Component={CountryField}
        label="Pays*"
        name="locationCountry"
        placeholder=""
        value={formData.locationCountry}
        onChange={handleChangeCountry}
        error={errors?.locationCountry}
        helpText={FORM_HELP_TEXT.locationCountry}
      />
      <CustomField
        Component={TextField}
        id="contactPhone"
        name="contactPhone"
        label="Téléphone*"
        onChange={handleChange}
        value={formData.contactPhone}
        error={errors?.contactPhone}
        style={{ maxWidth: "370px" }}
        helpText={FORM_HELP_TEXT.contactPhone}
      />
      <div data-scroll="consentCertification" />
      <CheckboxField
        name="consentCertification"
        label={FORM_HELP_TEXT.consentCertification}
        value={formData.consentCertification}
        onChange={handleCheckboxChange}
        style={{ fontSize: "14px" }}
      />
      {errors?.consentCertification && (
        <StaticToast style={{ marginTop: "0.5rem" }}>
          {errors.consentCertification}
        </StaticToast>
      )}
      <Spacer size="0.5rem" />
      {!hasNewsletter && (
        <>
          <CheckboxField
            name="subscribed2022"
            label="Recevoir les lettres d'information de la france insoumise"
            value={formData?.subscribed2022}
            onChange={handleCheckboxChange}
            style={{ fontSize: "14px" }}
          />
          <Spacer size="0.5rem" />
        </>
      )}
      <p style={{ fontSize: "14px" }}>
        Un reçu, édité par la CNCCFP, me sera adressé, et me permettra de
        déduire cette somme de mes impôts dans les limites fixées par la loi.
      </p>
      <Spacer size="1rem" />
      {!!Object.values(errors).filter((error) => !!error).length && (
        <>
          <StaticToast style={{ marginTop: "0.5rem" }}>
            Des erreurs sont présentes dans le formulaire, veuillez les résoudre
            avant de l'envoyer
          </StaticToast>
          <Spacer size="1rem" />
        </>
      )}
      <StepButton
        type="submit"
        disabled={isLoading}
        onClick={(e) => handleSubmit(e, cardPaymentMode)}
      >
        <span>
          <strong>Continuer</strong>
          <br />
          Paiement en ligne sécurisé
        </span>
        <RawFeatherIcon name="arrow-right" />
      </StepButton>
      {!!checkPaymentMode && (
        <>
          <Spacer size="1rem" />
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexDirection: "column",
            }}
          >
            ou
            <Spacer size="1rem" />
            <Button
              onClick={(e) => handleSubmit(e, checkPaymentMode)}
              disabled={isLoading}
            >
              Envoyer un chèque
            </Button>
          </div>
        </>
      )}
      <Spacer size="1rem" />
      <hr />
      <Legal type={type} />
    </form>
  );
};

InformationsStep.propTypes = {
  onSubmit: PropTypes.func,
  errors: PropTypes.object,
  setErrors: PropTypes.func,
  formData: PropTypes.object,
  setFormData: PropTypes.func,
  isLoading: PropTypes.bool,
  hidden: PropTypes.bool,
  type: PropTypes.string,
};

export default InformationsStep;
