import React, { useRef } from "react";
import PropTypes from "prop-types";

import { StepButton } from "./StyledComponents";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import StaticToast from "@agir/front/genericComponents/StaticToast";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import TextField from "@agir/front/formComponents/TextField";
import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import CountryField from "@agir/front/formComponents/CountryField";
import CustomField from "./CustomField";

const StyledPostalCodeTextField = styled(TextField)`
  max-width: 160px;
  width: 160px;
  @media (min-width: ${style.collapse}px) {
    margin-right: 130px;
  }
`;

const GroupedFields = styled.div`
  @media (max-width: ${style.collapse}px) {
    flex: 0 1;
    display: flex;
    flex-direction: row;
  }

  @media (max-width: 450px) {
    flex-direction: column;
  }
`;

const helpEmail =
  "Si vous êtes déjà inscrit·e sur lafranceinsoumise.fr ou melenchon2022.fr, utilisez l'adresse avec laquelle vous êtes inscrit·e";
const helpNationality =
  "Si double nationalité dont française : indiquez France";
const helpPhone =
  "Nous sommes dans l'obligation de pouvoir vous contacter en cas de demande de vérification par la CNCCFP.";
const consentText =
  "Je certifie sur l'honneur être une personne physique et que le réglement de mon don ne provient pas d'une personne morale (association, société, société civile...) mais de mon compte bancaire personnel.*";

const InformationsStep = ({
  onSubmit,
  errors,
  setErrors,
  formData,
  setFormData,
  isLoading,
}) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setErrors((error) => ({ ...error, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
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

  // Submit with payment_mode
  const handleSubmit = (e, value) => {
    setFormData({ ...formData, payment_mode: value }, () => {
      onSubmit(e);
    });
  };

  const checkPaymentMode = formData.allowedPaymentModes?.filter((value) =>
    value.includes("check")
  )[0];
  const cardPaymentMode = formData.allowedPaymentModes?.filter(
    (value) => !value.includes("check")
  )[0];

  return (
    <form onSubmit={onSubmit}>
      <CustomField
        Component={TextField}
        id="email"
        name="email"
        label="E-mail*"
        onChange={handleChange}
        value={formData.email}
        error={errors?.email}
        helpText={helpEmail}
      />

      <GroupedFields>
        <CustomField
          Component={TextField}
          id="firstName"
          name="firstName"
          label="Prénom*"
          onChange={handleChange}
          value={formData.firstName}
          error={errors?.firstName}
        />
        <CustomField
          Component={TextField}
          id="lastName"
          name="lastName"
          label="Nom de famille*"
          onChange={handleChange}
          value={formData.lastName}
          error={errors?.lastName}
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
        helpText={helpNationality}
      />

      {formData.nationality !== "FR" && (
        <>
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
        </>
      )}

      <CustomField
        Component={TextField}
        label="Adresse*"
        name="locationAddress1"
        value={formData.locationAddress1}
        onChange={handleChange}
        error={errors?.locationAddress1}
      />

      <GroupedFields>
        <CustomField
          Component={StyledPostalCodeTextField}
          label="Code postal*"
          name="locationZip"
          value={formData.locationZip}
          onChange={handleChange}
          error={errors?.locationZip}
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
        helpText={helpPhone}
      />

      <CheckboxField
        name="consentCertification"
        label={consentText}
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

      <CheckboxField
        name="subscribedLfi"
        label="Recevoir les lettres d'information de la France insoumise"
        value={formData?.subscribedLfi}
        onChange={handleCheckboxChange}
        style={{ fontSize: "14px" }}
      />
      <Spacer size="0.5rem" />

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
      <p style={{ fontSize: "13px", color: "#777777" }}>
        Premier alinéa de l’article 11-4 de la loi 88-227 du 11 mars 1988
        modifiée : une personne physique peut verser un don à un parti ou
        groupement politique si elle est de nationalité française ou si elle
        réside en France. Les dons consentis et les cotisations versées en
        qualité d’adhérent d’un ou de plusieurs partis ou groupements politiques
        par une personne physique dûment identifiée à une ou plusieurs
        associations agréées en qualité d’association de financement ou à un ou
        plusieurs mandataires financiers d’un ou de plusieurs partis ou
        groupements politiques ne peuvent annuellement excéder 7 500 euros.
        <Spacer size="0.5rem" />
        Troisième alinéa de l’article 11-4 : Les personnes morales à l’exception
        des partis ou groupements politiques ne peuvent contribuer au
        financement des partis ou groupements politiques, ni en consentant des
        dons, sous quelque forme que ce soit, à leurs associations de
        financement ou à leurs mandataires financiers, ni en leur fournissant
        des biens, services ou autres avantages directs ou indirects à des prix
        inférieurs à ceux qui sont habituellement pratiqués. Les personnes
        morales, à l’exception des partis et groupements politiques ainsi que
        des établissements de crédit et sociétés de financement ayant leur siège
        social dans un Etat membre de l’Union européenne ou partie à l’accord
        sur l’Espace économique européen, ne peuvent ni consentir des prêts aux
        partis et groupements politiques ni apporter leur garantie aux prêts
        octroyés aux partis et groupements politiques.
        <Spacer size="0.5rem" />
        Premier alinéa de l’article 11-5 : Les personnes qui ont versé un don ou
        consenti un prêt à un ou plusieurs partis ou groupements politiques en
        violation des articles 11-3-1 et 11-4 sont punies de trois ans
        d’emprisonnement et de 45 000 € d’amende.
      </p>
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
};

export default InformationsStep;
