import React, { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import Helmet from "react-helmet";
import useSWR from "swr";
import { useHistory } from "react-router-dom";

import { Theme } from "./StyledComponents";
import CONFIG from "./config";
import * as api from "./api";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import InformationsStep from "./InformationsStep";
import Breadcrumb from "./Breadcrumb";
import AmountInformations from "./AmountInformations";
import {
  StyledIllustration,
  StyledBody,
  StyledPage,
  StyledLogo,
  StyledMain,
  Title,
} from "./StyledComponents";
import { displayPrice } from "@agir/lib/utils/display";

import { routeConfig } from "@agir/front/app/routes.config";

const InformationsPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const { data: session } = useSWR("/api/session/");
  const { data: sessionDonation } = useSWR("/api/session/donation/");

  const history = useHistory();
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

  let amountStepUrl = routeConfig.donations.getLink(params);
  // Keep params in url
  if (!!groupPk) {
    amountStepUrl += `?group=${groupPk}`;
  }

  const externalLinkRoute =
    CONFIG[type]?.externalLinkRoute || CONFIG.default.externalLinkRoute;

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

  useEffect(() => {
    if (!sessionDonation) return;

    // Redirect to Amount Step if session not filled with an amount
    if (!sessionDonation?.donations?.amount) {
      history.push(amountStepUrl);
    }

    setFormData({
      ...formData,
      amount: sessionDonation?.donations?.amount,
      type: sessionDonation?.donations?.type,
      allocations: JSON.parse(sessionDonation?.donations?.allocations),
      allowedPaymentModes: JSON.parse(
        sessionDonation?.donations?.allowedPaymentModes || "[]"
      ),
    });
  }, [sessionDonation]);

  const amount = formData.amount;
  const groupAmount =
    Array.isArray(formData?.allocations) && formData.allocations[0]?.amount;
  const nationalAmount = amount - groupAmount;
  const amountString = displayPrice(amount);
  const groupAmountString = displayPrice(groupAmount);
  const nationalAmountString = displayPrice(nationalAmount);

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

                <Breadcrumb onClick={() => history.push(amountStepUrl)} />
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
