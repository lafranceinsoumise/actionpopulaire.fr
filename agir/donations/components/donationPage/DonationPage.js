import React, { useCallback, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import useSWR from "swr";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import AmountStep from "./AmountStep";
import { Theme } from "./StyledComponents";
import Modal from "@agir/front/genericComponents/Modal";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { InformationsStep } from "./InformationsStep";

import * as api from "./api";

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

// Return string from @amount in cents in string format. Example : 3050 => 30,5€
const displayAmount = (amount) =>
  parseInt(amount / 100) + "," + (amount % 100) + "€";

const DonationPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

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
    allocations: [],
    // informations
    email: session.user?.email || "",
    first_name: session.user?.firstName || "",
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

  const handleAmountSubmit = useCallback(async (data) => {
    setIsLoading(true);
    setErrors({});

    const { data: result, error } = await api.createDonation(data);

    setFormData({
      ...formData,
      ...result,
    });
    setShowModal(true);
    setIsLoading(false);

    if (error) {
      setErrors({
        amount: error?.amount || "Une erreur est survenue. Veuillez ressayer.",
      });
      return;
    }
    // window.location.href = result.data.next;
  }, []);

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

    console.log("Send donations result", data);

    setIsLoading(false);
    if (error) {
      setErrors(error);
      return;
    }
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
          error={errors?.amount}
          onSubmit={handleAmountSubmit}
        />

        <Modal shouldShow={showModal} onClose={closeModal}>
          <ModalContainer>
            <Title>Je donne {amountString}</Title>
            <Breadcrumb>
              <div onClick={closeModal}>1. Montant</div>
              <RawFeatherIcon name="chevron-right" width="1rem" height="1rem" />
              <div>2. Mes informations</div>
              <RawFeatherIcon name="chevron-right" width="1rem" height="1rem" />
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
                      <b>{groupAmountString}</b> pour le groupe {group?.name}
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
          </ModalContainer>
        </Modal>
      </PageFadeIn>
    </Theme>
  );
};

export default DonationPage;
