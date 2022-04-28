import React, { useCallback, useEffect, useRef, useState } from "react";
import { useLocation, useParams, useHistory } from "react-router-dom";
import styled from "styled-components";
import useSWR from "swr";

import { MANUAL_REVALIDATION_SWR_CONFIG } from "@agir/front/allPages/SWRContext";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Modal from "@agir/front/genericComponents/Modal";
import Spacer from "@agir/front/genericComponents/Spacer";
import AmountInformations from "./AmountInformations";
import Breadcrumb from "./Breadcrumb";
import OpenGraphTags from "@agir/front/app/OpenGraphTags";

import AmountStep from "./AmountStep";
import InformationsStep from "./InformationsStep";
import { Theme, Title } from "./StyledComponents";

import { scrollToError } from "@agir/front/app/utils";
import { displayPrice } from "@agir/lib/utils/display";
import { routeConfig } from "@agir/front/app/routes.config";

import CONFIG from "./config";
import * as api from "./api";

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

  const type = params?.type || "LFI";
  const config = CONFIG[type] || CONFIG.default;
  const isModalOpen = !!params.info;
  const groupPk = config.hasGroupAllocations && urlParams.get("group");

  const { data: session } = useSWR(
    "/api/session/",
    MANUAL_REVALIDATION_SWR_CONFIG
  );

  const {
    data: sessionDonation,
    mutate: mutateSessionDonation,
    error: sessionDonationError,
  } = useSWR("/api/session/donation/", MANUAL_REVALIDATION_SWR_CONFIG);

  const { data: group } = useSWR(
    groupPk && `/api/groupes/${groupPk}/`,
    MANUAL_REVALIDATION_SWR_CONFIG
  );

  const { data: userGroups } = useSWR(
    session?.user && type !== "2022" && "/api/groupes/",
    MANUAL_REVALIDATION_SWR_CONFIG
  );

  const [formData, setFormData] = useState({
    to: type,
    nationality: "FR",
    is2022: false,
    subscribed2022: false,
    frenchResident: true,
    consentCertification: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const scrollerRef = useRef(null);

  const amount = formData.amount;
  const groupAmount =
    Array.isArray(formData?.allocations) && formData.allocations[0]?.amount;

  const handleAmountSubmit = useCallback(
    async (data) => {
      setIsLoading(true);
      setErrors({});
      const { data: result, error } = await api.createDonation(data);
      setFormData((formData) => ({ ...formData, ...result }));
      setIsLoading(false);
      if (error) {
        setErrors({
          amount:
            error?.amount || "Une erreur est survenue. Veuillez ressayer.",
        });
        return;
      }
      history.replace(
        routeConfig.donations.getLink({
          type: type === "2022" ? type : undefined,
          info: "infos",
        }) + search
      );
    },
    [history, search, type]
  );

  const handleInformationsSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setIsLoading(true);
      setErrors({});

      const frontErrors = {};
      if (!formData.consentCertification) {
        frontErrors.consentCertification =
          "Vous devez cocher la case précédente pour continuer";
      }
      if (!formData.frenchResident) {
        frontErrors.frenchResident =
          "Si vous n'avez pas la nationalité française, vous devez être résident fiscalement en France pour faire une donation";
      }
      if (formData.nationality !== "FR" && formData.locationCountry !== "FR") {
        frontErrors.locationCountry =
          "Veuillez indiquer votre adresse fiscale en France.";
      }
      if (!formData.gender) {
        frontErrors.gender = "Ce champs ne peut pas être vide";
      }
      if (Object.keys(frontErrors).length > 0) {
        setIsLoading(false);
        setErrors(frontErrors);
        scrollToError(
          frontErrors,
          scrollerRef.current.parentElement.parentElement
        );
        return;
      }

      const { data, error } = await api.sendDonation({
        ...formData,
        allowedPaymentModes: undefined,
      });

      setIsLoading(false);

      if (error) {
        setErrors(error);
        scrollToError(error, scrollerRef.current.parentElement.parentElement);
        return;
      }

      window.location.href = data.next;
    },
    [formData]
  );

  const closeModal = useCallback(() => {
    history.replace(
      routeConfig.donations.getLink({
        type: type === "2022" ? type : undefined,
      }) + (groupPk ? `?group=${groupPk}` : "")
    );
  }, [history, groupPk, type]);

  useEffect(() => {
    isModalOpen && !amount && mutateSessionDonation();
  }, [amount, isModalOpen, mutateSessionDonation]);

  useEffect(() => {
    if (sessionDonationError) {
      closeModal();
      return;
    }
    if (!sessionDonation) {
      return;
    }
    if (!amount && !sessionDonation.donations?.amount) {
      closeModal();
      return;
    }
    setFormData((data) => ({
      ...data,
      amount: data.amount || sessionDonation.donations?.amount,
      paymentTimes:
        data.paymentTimes || sessionDonation.donations?.paymentTimes,
      allocations:
        data.allocations ||
        JSON.parse(sessionDonation.donations?.allocations || "[]"),
      paymentMode:
        data.paymentMode ||
        sessionDonation.donations?.paymentMode ||
        "system_pay",
      allowedPaymentModes:
        data.allowedPaymentModes ||
        sessionDonation.donations?.allowedPaymentModes ||
        "[]",
    }));
  }, [amount, sessionDonation, sessionDonationError, closeModal]);

  useEffect(() => {
    if (!session) {
      return;
    }
    setFormData((data) => ({
      ...data,
      email: data.email || session.user?.email || "",
      firstName: data.firstName || session.user?.firstName || "",
      lastName: data.lastName || session.user?.lastName || "",
      contactPhone: data.contactPhone || session.user?.contactPhone || "",
      locationAddress1: data.locationAddress1 || session.user?.address1 || "",
      locationAddress2: data.locationAddress2 || session.user?.address2 || "",
      locationZip: data.locationZip || session.user?.zip || "",
      locationCity: data.locationCity || session.user?.city || "",
      locationCountry: data.locationCountry || session.user?.country || "FR",
      gender:
        data.gender || ["M", "F"].includes(session.user?.gender)
          ? session.user.gender
          : "",
      is2022:
        typeof data.is2022 !== "undefined"
          ? data.is2022
          : session.user?.is2022 || "",
    }));
  }, [session]);

  return (
    <Theme type={formData.to} theme={config.theme}>
      <OpenGraphTags title={config.title} />
      <PageFadeIn ready={typeof session !== "undefined"} wait={<Skeleton />}>
        <AmountStep
          key={formData.amount + formData.paymentTimes}
          type={type}
          maxAmount={config.maxAmount}
          maxAmountWarning={config.maxAmountWarning}
          externalLinkRoute={config.externalLinkRoute}
          group={group?.isCertified ? group : null}
          hasGroups={
            Array.isArray(userGroups) &&
            userGroups.some((group) => group.isCertified)
          }
          isLoading={isLoading}
          error={errors?.amount}
          amountInit={formData.amount}
          byMonthInit={formData.paymentTimes === "M"}
          onSubmit={handleAmountSubmit}
        />

        <StyledModal shouldShow={isModalOpen} onClose={closeModal}>
          <ModalContainer ref={scrollerRef}>
            <Title>
              Je donne {displayPrice(amount)}{" "}
              {formData.paymentTimes === "M" && "par mois"}
            </Title>
            <Breadcrumb onClick={closeModal} />
            <Spacer size="1rem" />
            <AmountInformations
              group={group}
              total={displayPrice(amount)}
              amountGroup={displayPrice(groupAmount)}
              amountNational={displayPrice(amount - groupAmount)}
            />
            <InformationsStep
              formData={formData}
              setFormData={setFormData}
              hidden={!!session?.user?.email}
              errors={errors}
              setErrors={setErrors}
              isLoading={isLoading}
              onSubmit={handleInformationsSubmit}
              type={type}
            />
          </ModalContainer>
        </StyledModal>
      </PageFadeIn>
    </Theme>
  );
};

export default DonationPage;
