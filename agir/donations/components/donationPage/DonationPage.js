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
import { displayPrice } from "@agir/lib/utils/display";
import CONFIG from "./config";
import * as api from "./api";

const StyledModal = styled(Modal)`
  @media (min-width: ${style.collapse}px) {
    > div:first-of-type {
      margin-right: 14px;
      width: auto;
    }
  }
`;

const ModalContainer = styled.div`
  width: 70%;
  max-width: 740px;
  margin: 40px auto;
  margin-bottom: 40px;
  background-color: ${(props) => props.theme.white};
  padding: 40px;

  @media (min-width: ${style.collapse}px) {
    border-radius: ${style.borderRadius};
  }

  @media (max-width: ${style.collapse}px) {
    width: 100%;
    height: 100%;
    overflow-y: auto;
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
  const { data: sessionDonation } = useSWR("/api/session/donation/");

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
    to: type,
    amount: sessionDonation?.donations?.amount,
    type: sessionDonation?.donations?.type,
    allocations: JSON.parse(sessionDonation?.donations?.allocations || "[]"),
    // mode
    paymentMode: sessionDonation?.donations?.paymentMode || "system_pay",
    allowedPaymentModes: JSON.parse(
      sessionDonation?.donations?.allowedPaymentModes || "[]"
    ),
    // informations
    email: session?.user?.email || "",
    firstName: session?.user?.firstName || "",
    lastName: session?.user?.lastName || "",
    contactPhone: session?.user?.contactPhone || "",
    nationality: "FR",
    locationAddress1: session?.user?.address1 || "",
    locationZip: session?.user?.zip || "",
    locationCity: session?.user?.city || "",
    locationCountry: "FR",
    // checkboxes
    subscribedLfi: false,
    frenchResident: true,
    consentCertification: false,
  });

  const amount = formData.amount;
  const groupAmount =
    Array.isArray(formData?.allocations) && formData.allocations[0]?.amount;
  const nationalAmount = amount - groupAmount;
  const amountString = displayPrice(amount);
  const groupAmountString = displayPrice(groupAmount);
  const nationalAmountString = displayPrice(nationalAmount);

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

    if (!formData.consentCertification || !formData.frenchResident) {
      const frontErrors = {
        consentCertification:
          !formData.consentCertification &&
          "Vous devez cocher la case précédente pour continuer",
        frenchResident:
          !formData.frenchResident &&
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

        <StyledModal shouldShow={showModal} onClose={closeModal}>
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
        </StyledModal>
      </PageFadeIn>
    </Theme>
  );
};

export default DonationPage;
