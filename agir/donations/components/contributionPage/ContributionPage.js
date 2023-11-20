import React, { useCallback, useEffect } from "react";
import { useLocation, useParams, useHistory } from "react-router-dom";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";
import { useDonations } from "@agir/donations/common/hooks";
import ROUTES from "@agir/front/globalContext/nonReactRoutes.config";

import AmountStep from "./AmountStep";
import DonationForm from "@agir/donations/common/DonationForm";
import Modal from "@agir/front/genericComponents/Modal";
import OpenGraphTags from "@agir/front/app/OpenGraphTags";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
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

const ModalCloseButton = styled.div`
  display: none;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: block;
  }

  button {
    display: inline-block;
    height: 2.5rem;
    width: 2.5rem;
    background: transparent;
    border: none;
    text-align: left;
    padding: 0;
    cursor: pointer;
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

const TYPE = "contribution";

const ContributionPage = () => {
  const history = useHistory();
  const params = useParams();
  const { search } = useLocation();
  const urlParams = new URLSearchParams(search);

  const {
    config,
    formData,
    formErrors,
    isLoading,
    isReady,
    isRenewal,
    sessionUser,
    group,
    groups,
    updateFormData,
    handleSubmit,
    selectGroup,
  } = useDonations(TYPE, urlParams.get("group"), {
    amount: isNaN(parseInt(urlParams.get("amount")))
      ? 0
      : parseInt(urlParams.get("amount")),
  });

  const isModalOpen = params?.step === "validation";

  const { allowedPaymentModes, theme, title } = config;
  const { amount, paymentTiming } = formData;
  const paymentModes = allowedPaymentModes[paymentTiming];

  const openModal = useCallback(
    (amountData) => {
      Object.entries(amountData).forEach(([field, value]) => {
        updateFormData(field, value);
      });
      history.push(
        routeConfig.contributions.getLink({ step: "validation" }) + search,
      );
    },
    [history, search, updateFormData],
  );

  const closeModal = useCallback(() => {
    history.push(
      routeConfig.contributions.getLink({
        step: null,
      }) + search,
    );
  }, [history, search]);

  useEffect(() => {
    isModalOpen &&
      !amount &&
      history.replace(
        routeConfig.contributions.getLink({
          step: null,
        }) + search,
      );
  }, [amount, isModalOpen, history, search]);

  if (
    !isLoading &&
    !!sessionUser?.activeContribution &&
    !sessionUser.activeContribution.renewable
  ) {
    window.location.href = ROUTES.alreadyContributor;

    return null;
  }

  return (
    <Theme type={formData.to} theme={theme}>
      <OpenGraphTags title={title} />
      <PageFadeIn ready={isReady} wait={<Skeleton />}>
        {isReady && (
          <AmountStep
            {...config}
            group={group}
            isLoading={isLoading}
            error={formErrors.amount}
            initialAmount={formData.amount}
            initialPaymentTiming={formData.paymentTiming}
            initialAllocations={formData.allocations}
            onSubmit={openModal}
            groups={groups}
            selectGroup={selectGroup}
            effectDate={formData.effectDate}
            endDate={formData.endDate}
            isRenewal={isRenewal}
          />
        )}
        <StyledModal shouldShow={isModalOpen} onClose={closeModal}>
          <ModalContainer>
            <ModalCloseButton>
              <button
                type="button"
                onClick={closeModal}
                aria-label="Fermer la modale"
              >
                <RawFeatherIcon name="arrow-left" />
              </button>
            </ModalCloseButton>
            <DonationForm
              isLoading={isLoading}
              type={TYPE}
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

export default ContributionPage;
