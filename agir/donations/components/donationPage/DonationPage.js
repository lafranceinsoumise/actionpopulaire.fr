import React, { useCallback, useEffect } from "react";
import { useLocation, useParams, useHistory } from "react-router-dom";
import styled from "styled-components";
import useSWR from "swr";

import CONFIG from "@agir/donations/common/config";
import { MANUAL_REVALIDATION_SWR_CONFIG } from "@agir/front/allPages/SWRContext";

import { routeConfig } from "@agir/front/app/routes.config";
import { useDonations } from "@agir/donations/common/hooks";

import AmountStep from "./AmountStep";
import DonationForm from "@agir/donations/common/DonationForm";
import Modal from "@agir/front/genericComponents/Modal";
import OpenGraphTags from "@agir/front/app/OpenGraphTags";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { Theme } from "@agir/donations/common/StyledComponents";

const StyledModal = styled(Modal)`
  @media (min-width: ${(props) => props.theme.collapse}px) {
    & > div:first-of-type {
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

  @media (min-width: ${(props) => props.theme.collapse}px) {
    border-radius: ${(props) => props.theme.borderRadius};
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    width: 100%;
    height: 100%;
    overflow-y: auto;
    margin: 0;
    padding: 24px;
  }
`;

const DonationPage = () => {
  const history = useHistory();
  const params = useParams();
  const { search } = useLocation();
  const urlParams = new URLSearchParams(search);

  const {
    config,
    formData,
    formErrors,
    isLoading,
    sessionUser,
    updateFormData,
    handleSubmit,
  } = useDonations(params?.type, {
    amount: isNaN(parseInt(urlParams.get("amount")))
      ? 0
      : parseInt(urlParams.get("amount")),
  });

  const isModalOpen = params?.step === "validation";

  const { allowedPaymentModes, hasGroupAllocations, theme, title, type } =
    config;
  const { amount, paymentTimes } = formData;
  const paymentModes = allowedPaymentModes[paymentTimes];
  const groupPk = hasGroupAllocations && urlParams.get("group");

  const { data: group } = useSWR(
    groupPk && `/api/groupes/${groupPk}/`,
    MANUAL_REVALIDATION_SWR_CONFIG
  );

  const openModal = useCallback(
    (amountData) => {
      Object.entries(amountData).forEach(([field, value]) => {
        updateFormData(field, value);
      });
      history.replace(
        routeConfig.donations.getLink({
          type: params?.type,
          step: "validation",
        }) + search
      );
    },
    [history, search, params, updateFormData]
  );

  const closeModal = useCallback(() => {
    history.replace(
      routeConfig.donations.getLink({
        type: params?.type,
        step: null,
      }) + search
    );
  }, [history, search, params]);

  useEffect(() => {
    isModalOpen && !amount && closeModal();
  }, [amount, isModalOpen, closeModal]);

  useEffect(() => {
    if (!type || !CONFIG[type]) {
      history.replace(routeConfig.donations.getLink() + search);
    }
  }, [history, search, type]);

  return (
    <Theme type={formData.to} theme={theme}>
      <OpenGraphTags title={title} />
      <PageFadeIn
        ready={typeof sessionUser !== "undefined"}
        wait={<Skeleton />}
      >
        <AmountStep
          {...config}
          hasUser={!!sessionUser}
          group={group?.isCertified ? group : null}
          isLoading={isLoading}
          error={formErrors.amount}
          initialAmount={formData.amount}
          initialByMonth={formData.paymentTimes === "M"}
          onSubmit={openModal}
        />
        <StyledModal shouldShow={isModalOpen} onClose={closeModal}>
          <ModalContainer>
            <DonationForm
              isLoading={isLoading}
              type={type}
              formData={formData}
              formErrors={formErrors}
              groupName={group?.name}
              allowedPaymentModes={paymentModes}
              hideEmailField={!!sessionUser?.email}
              updateFormData={updateFormData}
              onSubmit={handleSubmit}
              onBack={closeModal}
            />
          </ModalContainer>
        </StyledModal>
      </PageFadeIn>
    </Theme>
  );
};

export default DonationPage;
