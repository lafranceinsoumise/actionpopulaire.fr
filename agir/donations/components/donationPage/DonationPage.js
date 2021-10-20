import React, { useCallback, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import Helmet from "react-helmet";
import useSWR from "swr";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Modal from "@agir/front/genericComponents/Modal";
import Spacer from "@agir/front/genericComponents/Spacer";
import AmountInformations from "./AmountInformations";
import Breadcrumb from "./Breadcrumb";
import AmountStep from "./AmountStep";
import InformationsStep from "./InformationsStep";

import { Theme, Title } from "./StyledComponents";
import { displayAmount } from "./utils";
import CONFIG from "./config";
import * as api from "./api";

const ModalContainer = styled.div`
  width: 70%;
  max-width: 740px;
  margin: 40px auto;
  margin-bottom: 40px;
  background-color: ${(props) => props.theme.white};
  padding: 40px;

  @media (max-width: ${style.collapse}px) {
    width: 100%;
    height: 100%;
    overflow-y: scroll;
    margin: 0;
    padding: 24px;
  }
`;

const DonationPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [showModal, setShowModal] = useState(false);
  const closeModal = () => setShowModal(false);

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

  const { data: userGroups } = useSWR(
    session?.user && type !== "2022" && "/api/groupes/",
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

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

  const handleAmountSubmit = useCallback(async (data) => {
    setIsLoading(true);
    setErrors({});

    const { data: result, error } = await api.createDonation(data);

    setFormData({
      ...formData,
      ...result,
    });
    setIsLoading(false);

    if (error) {
      setErrors({
        amount: error?.amount || "Une erreur est survenue. Veuillez ressayer.",
      });
      return;
    }

    setShowModal(true);

    // Redirect to informations step (keep group param in url)
    // window.location.href = result.next + (!!groupPk ? `?group=${groupPk}` : "");
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
        <AmountStep
          type={type}
          maxAmount={CONFIG[type]?.maxAmount || CONFIG.default.maxAmount}
          maxAmountWarning={
            CONFIG[type]?.maxAmountWarning || CONFIG.default.maxAmountWarning
          }
          externalLinkRoute={
            CONFIG[type]?.externalLinkRoute || CONFIG.default.externalLinkRoute
          }
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

            <Breadcrumb onClick={closeModal} />
            <Spacer size="1rem" />

            <AmountInformations
              group={group}
              total={amountString}
              amountGroup={groupAmountString}
              amountNational={nationalAmountString}
            />

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
