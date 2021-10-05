import React, { useCallback, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import useSWR from "swr";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

import AmountStep from "./AmountStep";
import { Link, StepButton, Theme } from "./StyledComponents";
import Modal from "@agir/front/genericComponents/Modal";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import { Hide } from "@agir/front/genericComponents/grid";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import TextField from "@agir/front/formComponents/TextField";
import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import CountryField from "@agir/front/formComponents/CountryField";

import { createDonation } from "./api";

const ModalContainer = styled.div`
  width: 70%;
  max-width: 740px;
  margin: 40px auto;
  margin-bottom: 40px;
  background-color: ${(props) => props.theme.white};
  padding: 20px 40px;

  @media (max-width: ${style.collapse}px) {
    width: 100%;
    height: 100%;
    overflow-y: scroll;
    margin: 0;
  }
`;

const Title = styled.h1`
  font-size: 28px;
`;

const Breadcrumb = styled.div`
  display: flex;
  align-items: center;

  @media (max-width: ${style.collapse}px) {
    font-size: 11px;
    span {
      margin: 2px;
      height: 11px;
      width: 11px;
    }
  }

  > div {
    cursor: pointer;
    color: ${(props) => props.theme.secondary500};
  }
  > div:nth-of-type(2) {
    color: ${(props) => props.theme.primary500};
  }
`;

const STextField = styled(TextField)``;

const StyledForm = styled.form`
  @media (min-width: ${style.collapse}px) {
    label {
      display: flex;
      flex: 0 1;
      align-items: center;
      span {
        width: 160px;
      }
      input {
        flex: 1;
        width: 100%;
      }
    }
  }

  ${STextField} {
    display: flex;
    background-color: orange;
  }
`;

const StyledDescription = styled.div`
  margin-left: 174px;
  font-size: 13px;
  margin-top: 4px;
  @media (max-width: ${style.collapse}px) {
    margin-top: 0;
    margin-bottom: 4px;
    margin-left: 0;
  }
`;

const helpEmail =
  "Si vous êtes déjà inscrit·e sur lafranceinsoumise.fr ou melenchon2022.fr, utilisez l'adresse avec laquelle vous êtes inscrit·e";
const helpNationality =
  "Si double nationalité dont française : indiquez française";
const helpPhone =
  "Nous sommes dans l'obligation de pouvoir vous contacter en cas de demande de vérification par la CNCCFP.";

const DonationPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const isDesktop = useIsDesktop();

  const { data: session } = useSWR("/api/session/");

  const params = useParams();
  const { search } = useLocation();
  const urlParams = new URLSearchParams(search);

  const type = params?.type || "LFI";
  const groupPk = type !== "melenchon2022" && urlParams.get("group");

  const { data: group } = useSWR(groupPk && `/api/groupes/${groupPk}/`, {
    revalidateIfStale: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });

  const { data: userGroups } = useSWR(
    session?.user && type !== "melenchon2022" && "/api/groupes/",
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

  const [showModal, setShowModal] = useState(true);
  const closeModal = () => setShowModal(false);

  const [formData, setFormData] = useState({
    // amounts
    amount: 500,
    to: type,
    type: "S",
    // personal informations
    email: "",
    firstName: "",
    lastName: "",
    phone: "",
    nationality: "",
    // address1: "",
    address: "",
    // zip: "",
    postalCode: "",
    city: "",
    country: "FR",
    // checkboxes
    consentCertification: false,
    newsletterLFI: false,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    // setError((error) => ({ ...error, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
  };

  const handleChangeCountry = (country) => {
    setFormData((formData) => ({ ...formData, country: country }));
  };

  const handleCheckboxChange = (e) => {
    setFormData((formData) => ({
      ...formData,
      [e.target.name]: e.target.checked,
    }));
  };

  const handleAmountSubmit = useCallback(async (data) => {
    setIsLoading(true);
    setError("");
    const result = await createDonation(data);

    setFormData({
      ...formData,
      amount: data.amount,
      type: data.type,
      to: data.to,
    });
    setShowModal(true);

    setIsLoading(false);
    if (result.error || !result?.data?.next) {
      setError(result.error || "Une erreur est survenue. Veuillez ressayer.");
      return;
    }
    // window.location.href = result.data.next;
  }, []);

  const handleInformationsSubmit = () => {
    console.log("TODO");
  };

  return (
    <Theme type={formData.to}>
      <PageFadeIn ready={typeof session !== "undefined"} wait={<Skeleton />}>
        <AmountStep
          type={type}
          group={group && group.isCertified ? group : null}
          hasGroups={
            Array.isArray(userGroups?.groups) &&
            userGroups.groups.some((group) => group.isCertified)
          }
          isLoading={isLoading}
          error={error}
          onSubmit={handleAmountSubmit}
        />

        <Modal shouldShow={showModal} onClose={closeModal}>
          <ModalContainer>
            <Title>
              Je donne {parseInt(formData.amount / 100)},{formData.amount % 100}{" "}
              euros
            </Title>
            <Breadcrumb>
              <div onClick={closeModal}>1. Montant</div>
              <RawFeatherIcon name="chevron-right" width="1rem" height="1rem" />
              <div>2. Mes informations</div>
              <RawFeatherIcon name="chevron-right" width="1rem" height="1rem" />
              <div>3. Paiement</div>
            </Breadcrumb>

            <Spacer size="1rem" />

            <StyledForm onSubmit={handleInformationsSubmit}>
              <TextField
                id="email"
                name="email"
                label="Adresse e-mail*"
                onChange={handleChange}
                value={formData.email}
                error={error?.email}
                helpText={!isDesktop && helpEmail}
              />
              <Hide under as={StyledDescription}>
                {helpEmail}
              </Hide>

              <Spacer size="1rem" />

              <TextField
                id="firstName"
                name="firstName"
                label="Prénom*"
                onChange={handleChange}
                value={formData.firstName}
                error={error?.firstName}
              />
              <Spacer size="1rem" />
              <TextField
                id="lastName"
                name="lastName"
                label="Nom de famille*"
                onChange={handleChange}
                value={formData.lastName}
                error={error?.lastName}
              />
              <Spacer size="1rem" />

              <CountryField
                label="Nationalité*"
                name="country"
                placeholder=""
                value={formData.country}
                onChange={handleChangeCountry}
                error={error?.country}
                helpText={!isDesktop && helpNationality}
              />
              <Hide under as={StyledDescription}>
                {helpNationality}
              </Hide>
              <Spacer size="1rem" />

              <TextField
                label="Adresse*"
                name="address"
                value={formData.address}
                onChange={handleChange}
                error={error?.address}
              />
              <Spacer size="1rem" />
              <TextField
                label="Code postal*"
                name="postalCode"
                value={formData.postalCode}
                onChange={handleChange}
                error={error?.postalCode}
                style={{ maxWidth: "160px" }}
              />
              <Spacer size="1rem" />
              <TextField
                label="Ville*"
                name="city"
                value={formData.city}
                onChange={handleChange}
                error={error?.city}
              />
              <Spacer size="1rem" />
              <CountryField
                label="Pays*"
                name="country"
                placeholder=""
                value={formData.country}
                onChange={handleChangeCountry}
                error={error?.country}
              />
              <Spacer size="1rem" />

              <TextField
                id="phone"
                name="phone"
                label="Téléphone*"
                onChange={handleChange}
                value={formData.phone}
                error={error?.phone}
                style={{ maxWidth: "370px" }}
                helpText={!isDesktop && helpPhone}
              />
              <Hide under as={StyledDescription}>
                {helpPhone}
              </Hide>
              <Spacer size="1rem" />

              <CheckboxField
                name="consentCertification"
                label="Je certifie sur l'honneur être une personne physique et que le réglement de mon don ne provient pas d'une personne morale (association, société, société civile...) mais de mon compte bancaire personnel.*"
                value={formData.consentCertification}
                error={error?.consentCertification}
                onChange={handleCheckboxChange}
              />
              <Spacer size="1rem" />

              <CheckboxField
                name="newsletterLFI"
                label="Recevoir les lettres d'information de la France insoumise"
                value={formData?.newsletterLFI}
                error={error?.newsletterLFI}
                onChange={handleCheckboxChange}
              />
              <Spacer size="1rem" />

              <p>
                Un reçu, édité par la CNCCFP, me sera adressé, et me permettra
                de déduire cette somme de mes impôts dans les limites fixées par
                la loi.
              </p>
              <Spacer size="1rem" />

              <StepButton type="submit" disabled={isLoading}>
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
                <Button>Envoyer un chèque</Button>
              </div>
              <Spacer size="1rem" />
            </StyledForm>

            <hr />
            <p style={{ fontSize: "13px", color: "#777777" }}>
              Premier alinéa de l’article 11-4 de la loi 88-227 du 11 mars 1988
              modifiée : une personne physique peut verser un don à un parti ou
              groupement politique si elle est de nationalité française ou si
              elle réside en France. Les dons consentis et les cotisations
              versées en qualité d’adhérent d’un ou de plusieurs partis ou
              groupements politiques par une personne physique dûment identifiée
              à une ou plusieurs associations agréées en qualité d’association
              de financement ou à un ou plusieurs mandataires financiers d’un ou
              de plusieurs partis ou groupements politiques ne peuvent
              annuellement excéder 7 500 euros.
              <Spacer size="0.5rem" />
              Troisième alinéa de l’article 11-4 : Les personnes morales à
              l’exception des partis ou groupements politiques ne peuvent
              contribuer au financement des partis ou groupements politiques, ni
              en consentant des dons, sous quelque forme que ce soit, à leurs
              associations de financement ou à leurs mandataires financiers, ni
              en leur fournissant des biens, services ou autres avantages
              directs ou indirects à des prix inférieurs à ceux qui sont
              habituellement pratiqués. Les personnes morales, à l’exception des
              partis et groupements politiques ainsi que des établissements de
              crédit et sociétés de financement ayant leur siège social dans un
              Etat membre de l’Union européenne ou partie à l’accord sur
              l’Espace économique européen, ne peuvent ni consentir des prêts
              aux partis et groupements politiques ni apporter leur garantie aux
              prêts octroyés aux partis et groupements politiques.
              <Spacer size="0.5rem" />
              Premier alinéa de l’article 11-5 : Les personnes qui ont versé un
              don ou consenti un prêt à un ou plusieurs partis ou groupements
              politiques en violation des articles 11-3-1 et 11-4 sont punies de
              trois ans d’emprisonnement et de 45 000 € d’amende.
            </p>
          </ModalContainer>
        </Modal>
      </PageFadeIn>
    </Theme>
  );
};

export default DonationPage;
