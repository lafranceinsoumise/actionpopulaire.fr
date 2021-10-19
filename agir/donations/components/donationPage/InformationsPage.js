import React, { useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import Helmet from "react-helmet";
import useSWR from "swr";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import { Theme } from "./StyledComponents";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import CONFIG from "./config";

import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { InformationsStep } from "./InformationsStep";
import {
  StyledIllustration,
  StyledBody,
  StyledPage,
  StyledLogo,
  StyledMain,
} from "./StyledComponents";

import * as api from "./api";

const Title = styled.h1`
  font-size: 28px;
  margin: 0;
`;

const Breadcrumb = styled.div`
  display: flex;
  align-items: center;
  margin-top: 1rem;

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
    font-weight: bold;
  }
  > div:nth-of-type(2) {
    color: ${(props) => props.theme.primary500};
  }
`;

const StyledAmountInformations = styled.div`
  padding: 1rem;
  background-color: ${(props) => props.theme.primary100};
  color: ${(props) => props.theme.primary500};
  border-radius: 4px;
  ul {
    margin: 0;
  }
`;

// Return string from @amount given in centimes. Example : 3050 => 30,5€
const displayAmount = (amount) =>
  parseInt(amount / 100) + "," + (amount % 100) + "€";

const InformationsPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const { data: session } = useSWR("/api/session/");

  const params = useParams();
  const { search } = useLocation();
  const urlParams = new URLSearchParams(search);

  const type = params?.type || "LFI";
  const groupPk = type !== "2022" && urlParams.get("group");

  const { data: group } = useSWR(groupPk && `/api/groupes/${groupPk}/`, {
    revalidateIfStale: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });

  const externalLinkRoute =
    CONFIG[type]?.externalLinkRoute || CONFIG.default.externalLinkRoute;

  const [formData, setFormData] = useState({
    // amounts
    amount: 500,
    to: type,
    type: "S",
    allocations: [],
    // informations
    email: session?.user?.email || "",
    first_name: session?.user?.firstName || "",
    last_name: "",
    contact_phone: "",
    nationality: "FR",
    location_address1: "",
    location_zip: "",
    location_city: "",
    location_country: "FR",
    // checkboxes
    subscribed_lfi: false,
    consent_certification: false,
    french_resident: true,
    // mode
    payment_mode: "system_pay",
  });

  const amount = formData.amount;
  const groupAmount =
    Array.isArray(formData?.allocations) && formData.allocations[0]?.amount;
  const nationalAmount = amount - groupAmount;
  const amountString = displayAmount(amount);
  const groupAmountString = displayAmount(groupAmount);
  const nationalAmountString = displayAmount(nationalAmount);

  const handleInformationsSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    if (!formData.consent_certification || !formData.french_resident) {
      const frontErrors = {
        consent_certification:
          !formData.consent_certification &&
          "Vous devez cocher la case précédente pour continuer",
        french_resident:
          !formData.french_resident &&
          "Si vous n'êtes pas de nationalité française, vous devez légalement être résident fiscalement pour faire cette donation",
      };
      setErrors(frontErrors);
      setIsLoading(false);
      return;
    }

    const { data, error } = await api.sendDonation(formData);

    setIsLoading(false);
    if (error) {
      setErrors(error);
      return;
    }

    window.location.href = data.next;
  };

  return (
    <Theme type={formData.to}>
      <Helmet>
        <title>{CONFIG[type]?.title || CONFIG.default.title}</title>
      </Helmet>

      <PageFadeIn ready={typeof session !== "undefined"} wait={<Skeleton />}>
        <StyledPage>
          <StyledIllustration aria-hidden="true" />
          <StyledBody>
            <StyledMain>
              <StyledLogo
                alt={`Logo ${
                  type === "2022" ? "Mélenchon 2022" : "la France insoumise"
                }`}
                route={externalLinkRoute}
                rel="noopener noreferrer"
                target="_blank"
              />

              <div>
                <Title>Je donne {amountString}</Title>
                <Breadcrumb>
                  <div onClick={() => {}}>1. Montant</div>
                  <RawFeatherIcon
                    name="chevron-right"
                    width="1rem"
                    height="1rem"
                  />
                  <div>2. Mes informations</div>
                  <RawFeatherIcon
                    name="chevron-right"
                    width="1rem"
                    height="1rem"
                  />
                  <div>3. Paiement</div>
                </Breadcrumb>

                <Spacer size="1rem" />

                {groupPk && (
                  <>
                    <StyledAmountInformations>
                      Je fais un don de <b>{amountString}</b> qui sera réparti :
                      <br />
                      <ul>
                        <li>
                          <b>{groupAmountString}</b> pour le groupe{" "}
                          {group?.name}
                        </li>
                        <li>
                          <b>{nationalAmountString}</b> pour les activités
                          nationales
                        </li>
                      </ul>
                    </StyledAmountInformations>
                    <Spacer size="1rem" />
                  </>
                )}

                <InformationsStep
                  formData={formData}
                  setFormData={setFormData}
                  errors={errors}
                  setErrors={setErrors}
                  isLoading={isLoading}
                  onSubmit={handleInformationsSubmit}
                />
                <Spacer size="2rem" />
              </div>
            </StyledMain>
          </StyledBody>
        </StyledPage>
      </PageFadeIn>
    </Theme>
  );
};

export default InformationsPage;
