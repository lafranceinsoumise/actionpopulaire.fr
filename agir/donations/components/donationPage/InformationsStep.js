import React, { useState } from "react";
import PropTypes from "prop-types";
import useSWR from "swr";

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
  font-size: 1rem;
  text-align: left;
  font-weight: 400;
  width: auto;
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
  hidden = false,
  type = "",
}) => {
  const [hasAddress2, setHasAddress2] = useState(false);

  const { data: profile } = useSWR("/api/user/profile/");
  let hasNewsletter = false;
  if (profile?.newsletters && Array.isArray(profile.newsletters)) {
    if (
      profile.newsletters.includes("2022") &&
      profile.newsletters.includes("2022_exceptionnel")
    ) {
      hasNewsletter = true;
    }
  }

  const displayAddress2 = () => {
    setHasAddress2(true);
  };

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
        helpText={helpEmail}
        hidden={hidden}
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
      />

      {hasAddress2 || formData.locationAddress2 || errors.locationAddress2 ? (
        <CustomField
          Component={TextField}
          label=""
          name="locationAddress2"
          value={formData.locationAddress2}
          onChange={handleChange}
          error={errors?.locationAddress2}
        />
      ) : (
        <div style={{ paddingBottom: "1rem" }}>
          <StyledButton type="button" onClick={displayAddress2}>
            + Ajouter une deuxième ligne pour l'adresse
          </StyledButton>
        </div>
      )}

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

      <div data-scroll="consentCertification" />
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

      {!hasNewsletter && (
        <>
          <CheckboxField
            name="subscribed2022"
            label="Recevoir les lettres d'information de la campagne Mélenchon 2022"
            value={formData?.subscribed2022}
            onChange={handleCheckboxChange}
            style={{ fontSize: "14px" }}
          />
          <Spacer size="0.5rem" />
        </>
      )}

      {!profile?.is2022 && (
        <>
          <CheckboxField
            name="is2022"
            label="Je soutiens la candidature de Jean-Luc Mélenchon pour 2022"
            value={formData?.is2022}
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
      <p style={{ fontSize: "13px", color: "#777777" }}>
        {type === "2022" ? (
          <>
            Les dons sont destinés à l'
            <strong>
              <abbr title="Association de Financement de la Campagne Présidentielle de Jean-Luc Mélenchon 2022">
                AFCP JLM 2022
              </abbr>
            </strong>
            , déclarée à la préfecture de Paris le 15 juin 2021, seule habilitée
            à recevoir les dons en faveur du candidat Jean-Luc Mélenchon, dans
            le cadre de la campagne pour l'élection présidentielle de 2022.
            <Spacer size="0.5rem" />
            Un reçu détaché d'une formule numérotée éditée par la Commission
            nationale des comptes de campagne vous sera directement adressé en
            mai de l’année suivant l’année de versement de votre don.
            <Spacer size="0.5rem" />
            Tout don de personne morale (entreprise, association, SCI, compte
            professionnel de professions libérales ou de commerçants…) est
            interdit.
            <Spacer size="0.5rem" />
            <strong>
              Alinéa 1, 2 et 3 de l'article L. 52-8 du Code électoral :
            </strong>
            <Spacer size="0.5rem" />
            Une personne physique peut verser un don à un candidat si elle est
            de nationalité française ou si elle réside en France. Les dons
            consentis par une personne physique dûment identifiée pour le
            financement de la campagne d'un ou plusieurs candidats lors des
            mêmes élections ne peuvent excéder 4 600 euros. Les personnes
            morales, à l'exception des partis ou groupements politiques, ne
            peuvent participer au financement de la campagne électorale d'un
            candidat, ni en lui consentant des dons sous quelque forme que ce
            soit, ni en lui fournissant des biens, services ou autres avantages
            directs ou indirects à des prix inférieurs à ceux qui sont
            habituellement pratiqués. [...] Tout don de plus de 150 euros
            consenti à un candidat en vue de sa campagne doit être versé par
            chèque, virement, prélèvement automatique ou carte bancaire.
            <Spacer size="0.5rem" />
            <strong>III. de l'article L113-1 du Code électoral :</strong>
            <Spacer size="0.5rem" />
            Sera puni de trois ans d'emprisonnement et de 45 000 € d'amende
            quiconque aura, en vue d'une campagne électorale, accordé un don ou
            un prêt en violation des articles L. 52-7-1 et L. 52-8.
          </>
        ) : (
          <>
            <strong>Premier alinéa de l’article 11-4</strong> de la loi 88-227
            du 11 mars 1988 modifiée : une personne physique peut verser un don
            à un parti ou groupement politique si elle est de nationalité
            française ou si elle réside en France. Les dons consentis et les
            cotisations versées en qualité d’adhérent d’un ou de plusieurs
            partis ou groupements politiques par une personne physique dûment
            identifiée à une ou plusieurs associations agréées en qualité
            d’association de financement ou à un ou plusieurs mandataires
            financiers d’un ou de plusieurs partis ou groupements politiques ne
            peuvent annuellement excéder 7 500 euros.
            <Spacer size="0.5rem" />
            <strong>Troisième alinéa de l’article 11-4 :</strong> Les personnes
            morales à l’exception des partis ou groupements politiques ne
            peuvent contribuer au financement des partis ou groupements
            politiques, ni en consentant des dons, sous quelque forme que ce
            soit, à leurs associations de financement ou à leurs mandataires
            financiers, ni en leur fournissant des biens, services ou autres
            avantages directs ou indirects à des prix inférieurs à ceux qui sont
            habituellement pratiqués. Les personnes morales, à l’exception des
            partis et groupements politiques ainsi que des établissements de
            crédit et sociétés de financement ayant leur siège social dans un
            Etat membre de l’Union européenne ou partie à l’accord sur l’Espace
            économique européen, ne peuvent ni consentir des prêts aux partis et
            groupements politiques ni apporter leur garantie aux prêts octroyés
            aux partis et groupements politiques.
            <Spacer size="0.5rem" />
            <strong>Premier alinéa de l’article 11-5 :</strong> Les personnes
            qui ont versé un don ou consenti un prêt à un ou plusieurs partis ou
            groupements politiques en violation des articles 11-3-1 et 11-4 sont
            punies de trois ans d’emprisonnement et de 45 000 € d’amende.
          </>
        )}
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
