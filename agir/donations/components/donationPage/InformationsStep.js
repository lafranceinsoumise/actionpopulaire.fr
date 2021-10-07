import React from "react";
import PropTypes from "prop-types";

import { StepButton } from "./StyledComponents";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import Toast from "@agir/front/genericComponents/Toast";

import { Hide } from "@agir/front/genericComponents/grid";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import TextField from "@agir/front/formComponents/TextField";
import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import CountryField from "@agir/front/formComponents/CountryField";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledPostalCodeTextField = styled(TextField)`
  max-width: 160px;
  width: 160px;
  @media (min-width: ${style.collapse}px) {
    margin-right: 130px;
  }
`;

const StyledDescription = styled.div`
  margin-left: 168px;
  font-size: 13px;
  @media (max-width: ${style.collapse}px) {
    margin-bottom: 4px;
    margin-left: 0;
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

const StyledCustomField = styled.div`
  @media (min-width: ${style.collapse}px) {
    display: flex;
    align-items: center;
    > label:first-of-type {
      width: 160px;
      margin: 0;
      margin-right: 4px;
    }
    > label:nth-of-type(2) {
      flex-grow: 1;
    }
  }
`;

const helpEmail =
  "Si vous êtes déjà inscrit·e sur lafranceinsoumise.fr ou melenchon2022.fr, utilisez l'adresse avec laquelle vous êtes inscrit·e";
const helpNationality =
  "Si double nationalité dont française : indiquez France";
const helpPhone =
  "Nous sommes dans l'obligation de pouvoir vous contacter en cas de demande de vérification par la CNCCFP.";

const CustomField = ({
  Component,
  noSpacer = false,
  id,
  label,
  helpText,
  ...rest
}) => {
  const isDesktop = useIsDesktop();

  return (
    <>
      <StyledCustomField htmlFor={id}>
        <Hide under as="label">
          {label}
        </Hide>
        <Component
          {...rest}
          label={(!isDesktop && label) || ""}
          helpText={(!isDesktop && helpText) || ""}
        />
      </StyledCustomField>
      {!!helpText && (
        <Hide under as={StyledDescription}>
          {helpText}
        </Hide>
      )}
      {!noSpacer && <Spacer size="0.5rem" />}
    </>
  );
};

CustomField.propTypes = {
  Component: PropTypes.elementType.isRequired,
  id: PropTypes.oneOf(["number", "string"]),
  label: PropTypes.string,
  helpText: PropTypes.string,
  noSpacer: PropTypes.bool,
};

export const InformationsStep = ({
  onSubmit,
  errors,
  setErrors,
  formData,
  setFormData,
  isLoading,
}) => {
  const isDesktop = useIsDesktop();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setErrors((error) => ({ ...error, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
  };

  const handleChangeCountry = (country) => {
    setFormData((formData) => ({ ...formData, location_country: country }));
  };

  const handleChangeNationality = (country) => {
    setFormData((formData) => ({
      ...formData,
      nationality: country,
      french_resident: country === "FR",
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

  return (
    <form onSubmit={onSubmit}>
      <CustomField
        Component={TextField}
        id="email"
        name="email"
        label="Adresse e-mail*"
        onChange={handleChange}
        value={formData.email}
        error={errors?.email}
        helpText={helpEmail}
      />

      <GroupedFields>
        <CustomField
          Component={TextField}
          id="first_name"
          name="first_name"
          label="Prénom*"
          onChange={handleChange}
          value={formData.first_name}
          error={errors?.first_name}
        />
        <CustomField
          Component={TextField}
          id="last_name"
          name="last_name"
          label="Nom de famille*"
          onChange={handleChange}
          value={formData.last_name}
          error={errors?.last_name}
          noSpacer
        />
      </GroupedFields>
      <Spacer size="0.5rem" />

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
            name="french_resident"
            label="Je certifie être domicilié⋅e fiscalement en France*"
            value={formData.french_resident}
            onChange={handleCheckboxChange}
          />
          {errors?.french_resident && (
            <Toast style={{ marginTop: "0.5rem" }}>
              {errors?.french_resident}
            </Toast>
          )}
          <Spacer size="0.5rem" />
        </>
      )}

      <CustomField
        Component={TextField}
        label="Adresse*"
        name="location_address1"
        value={formData.location_address1}
        onChange={handleChange}
        error={errors?.location_address1}
      />

      <GroupedFields>
        <CustomField
          Component={StyledPostalCodeTextField}
          label="Code postal*"
          name="location_zip"
          value={formData.location_zip}
          onChange={handleChange}
          error={errors?.location_zip}
          noSpacer
        />
        <Spacer size="0.5rem" />
        <CustomField
          Component={TextField}
          label="Ville*"
          name="location_city"
          value={formData.location_city}
          onChange={handleChange}
          error={errors?.location_city}
          noSpacer
          style={{ width: "100%" }}
        />
      </GroupedFields>
      <Spacer size="0.5rem" />

      <CustomField
        Component={CountryField}
        label="Pays*"
        name="location_country"
        placeholder=""
        value={formData.location_country}
        onChange={handleChangeCountry}
        error={errors?.location_country}
      />

      <CustomField
        Component={TextField}
        id="contact_phone"
        name="contact_phone"
        label="Téléphone*"
        onChange={handleChange}
        value={formData.contact_phone}
        error={errors?.contact_phone}
        style={{ maxWidth: "370px" }}
        helpText={helpPhone}
      />

      <CheckboxField
        name="consent_certification"
        label="Je certifie sur l'honneur être une personne physique et que le réglement de mon don ne provient pas d'une personne morale (association, société, société civile...) mais de mon compte bancaire personnel.*"
        value={formData.consent_certification}
        onChange={handleCheckboxChange}
      />
      {errors?.consent_certification && (
        <Toast style={{ marginTop: "0.5rem" }}>
          {errors?.consent_certification}
        </Toast>
      )}
      <Spacer size="1rem" />

      <CheckboxField
        name="subscribed_lfi"
        label="Recevoir les lettres d'information de la France insoumise"
        value={formData?.subscribed_lfi}
        onChange={handleCheckboxChange}
      />
      <Spacer size="1rem" />

      <p>
        Un reçu, édité par la CNCCFP, me sera adressé, et me permettra de
        déduire cette somme de mes impôts dans les limites fixées par la loi.
      </p>
      <Spacer size="1rem" />

      <StepButton
        type="submit"
        disabled={isLoading}
        onClick={(e) => handleSubmit(e, "system_pay")}
      >
        <span>
          <strong>Suivant</strong>
          <br />
          2/3 étapes
        </span>
        <RawFeatherIcon name="arrow-right" />
      </StepButton>

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
          onClick={(e) => handleSubmit(e, "check_donation")}
          disabled={isLoading}
        >
          Envoyer un chèque
        </Button>
      </div>
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
