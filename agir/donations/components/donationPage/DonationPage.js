import React, {
  useCallback,
  useState,
  useRef,
  useEffect,
  useMemo,
} from "react";
import {
  useLocation,
  useParams,
  useHistory,
  useRouteMatch,
} from "react-router-dom";
import useSWR from "swr";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

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
import CONFIG from "./config";
import * as api from "./api";
import { routeConfig } from "@agir/front/app/routes.config";

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

  const scrollerRef = useRef(null);
  const history = useHistory();

  const { data: session } = useSWR("/api/session/");
  const { data: sessionDonation } = useSWR("/api/session/donation/");

  const params = useParams();
  const { search } = useLocation();
  const urlParams = new URLSearchParams(search);

  const type = params?.type || "LFI";
  const groupPk = type !== "2022" && urlParams.get("group");

  const MODAL_ROUTE = routeConfig.donationsInformationsModal.getLink({
    type: type === "2022" ? type : undefined,
  });

  const isModalOpen = useMemo(() => useRouteMatch(MODAL_ROUTE), []);

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
    allowedPaymentModes:
      sessionDonation?.donations?.allowedPaymentModes || "[]",
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

  const closeModal = () => {
    history.push(
      routeConfig.donations.getLink({
        type: type === "2022" ? type : undefined,
      }) + (groupPk ? `?group=${groupPk}` : "")
    );
  };

  useEffect(() => {
    if (isModalOpen && !amount) {
      closeModal();
    }
  }, []);

  useEffect(() => {
    setFormData((formData) => ({
      ...formData,
      amount: sessionDonation?.donations?.amount,
      type: sessionDonation?.donations?.type,
      allocations: JSON.parse(sessionDonation?.donations?.allocations || "[]"),
      paymentMode: sessionDonation?.donations?.paymentMode || "system_pay",
      allowedPaymentModes:
        sessionDonation?.donations?.allowedPaymentModes || "[]",
    }));
  }, [sessionDonation]);

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

      history.push(MODAL_ROUTE + (groupPk ? `?group=${groupPk}` : ""));

      // Redirect to informations step (keep group param in url)
      // window.location.href = result.next + (!!groupPk ? `?group=${groupPk}` : "");
    },
    [type, history]
  );

  const handleInformationsSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    if (!formData.consentCertification || !formData.frenchResident) {
      const frontErrors = {};
      !formData.consentCertification &&
        (frontErrors.consentCertification =
          "Vous devez cocher la case précédente pour continuer");
      !formData.frenchResident &&
        (frontErrors.frenchResident =
          "Si vous n'êtes pas de nationalité française, vous devez légalement être résident fiscalement pour faire cette donation");

      setIsLoading(false);
      setErrors(frontErrors);
      scrollToError(
        frontErrors,
        scrollerRef.current.parentElement.parentElement
      );
      return;
    }

    const { data, error } = await api.sendDonation(formData);

    setIsLoading(false);

    if (error) {
      setErrors(error);
      scrollToError(error, scrollerRef.current.parentElement.parentElement);
      return;
    }

    window.location.href = data.next;
  };

  return (
    <Theme
      type={formData.to}
      theme={CONFIG[type]?.theme || CONFIG.default.theme}
    >
      <OpenGraphTags title={CONFIG[type]?.title || CONFIG.default.title} />
      <PageFadeIn ready={typeof session !== "undefined"} wait={<Skeleton />}>
        <AmountStep
          key={formData.amount + formData.type}
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
          amountInit={formData.amount}
          byMonthInit={formData.type === "M"}
          onSubmit={handleAmountSubmit}
        />

        <StyledModal shouldShow={isModalOpen} onClose={closeModal}>
          <ModalContainer ref={scrollerRef}>
            <Title>
              Je donne {amountString} {formData.type === "M" && "par mois"}
            </Title>

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
