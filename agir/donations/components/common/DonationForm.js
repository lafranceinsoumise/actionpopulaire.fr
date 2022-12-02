import React, { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import { displayPrice } from "@agir/lib/utils/display";
import { scrollToError } from "@agir/front/app/utils";
import { GENDER_OPTIONS, MONTHLY_PAYMENT } from "./form.config";

import AllocationDetails from "@agir/donations/common/AllocationDetails";
import Breadcrumb from "@agir/donations/common/Breadcrumb";
import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import CountryField from "@agir/front/formComponents/CountryField";
import CustomField from "@agir/donations/common/CustomField";
import DepartementField from "@agir/front/formComponents/DepartementField";
import Legal from "@agir/donations/common/Legal";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import SelectField from "@agir/front/formComponents/SelectField";
import Spacer from "@agir/front/genericComponents/Spacer";
import StaticToast from "@agir/front/genericComponents/StaticToast";
import { StepButton, Title } from "@agir/donations/common/StyledComponents";
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
  departement:
    "Indiquez le département auquel vous souhaitez reserver une partie de votre contribution",
  email:
    "Si vous êtes déjà inscrit·e sur lafranceinsoumise.fr, utilisez l'adresse avec laquelle vous êtes inscrit·e",
  nationality: "Si double nationalité dont française : indiquez France",
  contactPhone:
    "Nous sommes dans l'obligation de pouvoir vous contacter en cas de demande de vérification par la CNCCFP.",
  consentCertification:
    "Je certifie sur l'honneur être une personne physique et que le réglement de mon don ne provient pas d'une personne morale (association, société, société civile...) mais de mon compte bancaire personnel.*",
};

const DonationForm = ({
  type = "",
  formData,
  formErrors,
  isLoading,
  allowedPaymentModes,
  groupName,
  hideEmailField = false,
  updateFormData,
  onSubmit,
  onBack,
}) => {
  const [hasAddress2, setHasAddress2] = useState(false);

  const displayAddress2 = () => {
    setHasAddress2(true);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    updateFormData(name, value);
  };
  const handleCheck = (e) => {
    const { name, checked } = e.target;
    updateFormData(name, checked);
  };
  const handleChangeGender = (choice) => {
    updateFormData("gender", choice.value);
  };
  const handleChangeDepartement = (departement) => {
    updateFormData("departement", departement);
  };
  const handleChangeCountry = (country) => {
    updateFormData("locationCountry", country);
  };
  const handleChangeNationality = (country) => {
    updateFormData("nationality", country);
    updateFormData("frenchResident", country === "FR");
  };

  const hasMonthlyPayment = formData.paymentTiming === MONTHLY_PAYMENT;

  const hasCheck =
    Array.isArray(allowedPaymentModes) &&
    allowedPaymentModes.find((value) => value.includes("check"));

  const hasCard =
    Array.isArray(allowedPaymentModes) &&
    allowedPaymentModes.find((value) => !value.includes("check"));

  const scrollToErrorRef = useRef(null);
  const shouldScrollToError = useRef(false);

  const handleSubmit = (paymentMode) => () => {
    shouldScrollToError.current = true;
    onSubmit(paymentMode);
  };

  useEffect(() => {
    if (shouldScrollToError.current) {
      scrollToError(formErrors, scrollToErrorRef.current);
      shouldScrollToError.current = false;
    }
  }, [formErrors]);

  return (
    <div ref={scrollToErrorRef}>
      <Title>
        Je donne {displayPrice(formData.amount)}{" "}
        {hasMonthlyPayment && "par mois"}
      </Title>
      <Breadcrumb onClick={onBack} />
      <Spacer size="1rem" />
      <AllocationDetails
        groupName={groupName}
        byMonth={hasMonthlyPayment}
        totalAmount={formData.amount}
        allocations={formData.allocations}
      />
      <Spacer size="1rem" />
      <div>
        {!hideEmailField && (
          <CustomField
            Component={TextField}
            id="email"
            name="email"
            label="E-mail*"
            onChange={handleChange}
            value={formData.email}
            error={formErrors?.email}
            helpText={FORM_HELP_TEXT.email}
          />
        )}
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
            error={formErrors?.gender}
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
            error={formErrors?.firstName}
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
            error={formErrors?.lastName}
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
          error={formErrors?.nationality}
          helpText={FORM_HELP_TEXT.nationality}
        />
        {formData.nationality !== "FR" && (
          <div data-scroll="frenchResident">
            <CheckboxField
              name="frenchResident"
              label="Je certifie être domicilié⋅e fiscalement en France*"
              value={formData.frenchResident}
              onChange={handleCheck}
            />
            {formErrors?.frenchResident && (
              <StaticToast style={{ marginTop: "0.5rem" }}>
                {formErrors?.frenchResident}
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
          error={formErrors?.locationAddress1}
          helpText={FORM_HELP_TEXT.locationAddress1}
          noSpacer
        />
        {hasAddress2 ||
        formData.locationAddress2 ||
        formErrors?.locationAddress2 ? (
          <>
            <Spacer size="0.5rem" />
            <CustomField
              Component={TextField}
              label=""
              name="locationAddress2"
              value={formData.locationAddress2}
              onChange={handleChange}
              error={formErrors?.locationAddress2}
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
            error={formErrors?.locationZip}
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
            error={formErrors?.locationCity}
            helpText={FORM_HELP_TEXT.locationCity}
            noSpacer
            style={{ width: "100%" }}
          />
        </GroupedFields>
        <Spacer size="1rem" />
        <CustomField
          Component={DepartementField}
          label="Département*"
          name="departement"
          placeholder=""
          value={formData.departement}
          onChange={handleChangeDepartement}
          error={formErrors?.departement}
          helpText={FORM_HELP_TEXT.departement}
        />
        <Spacer size="1rem" />
        <CustomField
          Component={CountryField}
          label="Pays*"
          name="locationCountry"
          placeholder=""
          value={formData.locationCountry}
          onChange={handleChangeCountry}
          error={formErrors?.locationCountry}
          helpText={FORM_HELP_TEXT.locationCountry}
        />
        <CustomField
          Component={TextField}
          id="contactPhone"
          name="contactPhone"
          label="Téléphone*"
          onChange={handleChange}
          value={formData.contactPhone}
          error={formErrors?.contactPhone}
          style={{ maxWidth: "370px" }}
          helpText={FORM_HELP_TEXT.contactPhone}
        />
        <div data-scroll="consentCertification" />
        <CheckboxField
          name="consentCertification"
          label={FORM_HELP_TEXT.consentCertification}
          value={formData.consentCertification}
          onChange={handleCheck}
          style={{ fontSize: "14px" }}
        />
        {formErrors?.consentCertification && (
          <StaticToast style={{ marginTop: "0.5rem" }}>
            {formErrors.consentCertification}
          </StaticToast>
        )}
        <Spacer size="0.5rem" />
        <p style={{ fontSize: "14px" }}>
          Un reçu, édité par la CNCCFP, me sera adressé, et me permettra de
          déduire cette somme de mes impôts dans les limites fixées par la loi.
        </p>
        <Spacer size="1rem" />
        {formErrors &&
          !!Object.values(formErrors).filter((error) => !!error).length && (
            <>
              <StaticToast style={{ marginTop: "0.5rem" }}>
                {formErrors?.global ||
                  "Des erreurs sont présentes dans le formulaire, veuillez les résoudre avant de l'envoyer"}
              </StaticToast>
              <Spacer size="1rem" />
            </>
          )}
        <StepButton disabled={isLoading} onClick={handleSubmit(hasCard)}>
          <span>
            <strong>Continuer</strong>
            <br />
            Paiement en ligne sécurisé
          </span>
          <RawFeatherIcon name="arrow-right" />
        </StepButton>
        {!!hasCheck && (
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
              <Button disabled={isLoading} onClick={handleSubmit(hasCheck)}>
                {hasMonthlyPayment
                  ? "Payer en une seule fois par chèque"
                  : "Envoyer un chèque"}
              </Button>
            </div>
          </>
        )}
        <Spacer size="1rem" />
        <hr />
        <Legal type={type} />
      </div>
    </div>
  );
};

DonationForm.propTypes = {
  type: PropTypes.string,
  formData: PropTypes.object,
  formErrors: PropTypes.object,
  allowedPaymentModes: PropTypes.array,
  groupName: PropTypes.string,
  isLoading: PropTypes.bool,
  hideEmailField: PropTypes.bool,
  onBack: PropTypes.func,
  onSubmit: PropTypes.func,
  updateFormData: PropTypes.func,
};

export default DonationForm;
