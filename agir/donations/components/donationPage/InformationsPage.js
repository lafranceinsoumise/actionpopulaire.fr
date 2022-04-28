import React, { useEffect, useState, useRef } from "react";
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
import { scrollToError } from "@agir/front/app/utils";

import { routeConfig } from "@agir/front/app/routes.config";
import { MANUAL_REVALIDATION_SWR_CONFIG } from "@agir/front/allPages/SWRContext";

const InformationsPage = () => {
  const history = useHistory();
  const params = useParams();
  const { search, pathname } = useLocation();
  const urlParams = new URLSearchParams(search);

  const type = params?.type || "LFI";
  const config = CONFIG[type] || CONFIG.default;
  const groupPk = config.hasGroupAllocations && urlParams.get("group");
  const amountParam = urlParams.get("amount") || 0;
  const paymentTimes = pathname.includes("mensuels") ? "M" : "S";

  const [formData, setFormData] = useState({
    to: type,
    amount: amountParam || undefined,
    paymentTimes: paymentTimes,
    allocations: JSON.parse(sessionDonation?.donations?.allocations || "[]"),
    allowedPaymentModes: config.allowedPaymentModes[paymentTimes],
    nationality: "FR",
    is2022: false,
    subscribed2022: false,
    frenchResident: true,
    consentCertification: false,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const scrollerRef = useRef(null);

  const { data: session } = useSWR(
    "/api/session/",
    MANUAL_REVALIDATION_SWR_CONFIG
  );
  const { data: sessionDonation } = useSWR(
    "/api/session/donation/",
    MANUAL_REVALIDATION_SWR_CONFIG
  );
  const { data: group } = useSWR(
    groupPk && `/api/groupes/${groupPk}/`,
    MANUAL_REVALIDATION_SWR_CONFIG
  );

  const amountStepUrl = routeConfig.donations.getLink(params) + search;
  const externalLinkRoute = config.externalLinkRoute;
  const amount = formData.amount;
  const groupAmount =
    Array.isArray(formData?.allocations) && formData.allocations[0]?.amount;
  const nationalAmount = amount - groupAmount;

  const handleInformationsSubmit = async (e) => {
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
      scrollToError(error, scrollerRef.current);
      return;
    }

    window.location.href = data.next;
  };

  useEffect(() => {
    if (!sessionDonation) return;
    // Redirect to Amount Step if session not filled with an amount
    if (!sessionDonation?.donations?.amount && !amount) {
      history.replace(amountStepUrl);
      return;
    }
    setFormData((data) => ({
      ...data,
      amount: data.amount || sessionDonation.donations.amount,
      allocations: JSON.parse(sessionDonation?.donations?.allocations || "[]"),
      paymentMode: sessionDonation?.donations?.paymentMode || "system_pay",
    }));
  }, [history, amountStepUrl, amount, sessionDonation]);

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
    <Theme type={formData.to}>
      <Helmet>
        <title>{config.title}</title>
      </Helmet>

      <PageFadeIn ready={typeof session !== "undefined"} wait={<Skeleton />}>
        <StyledPage>
          <StyledIllustration aria-hidden="true" />
          <StyledBody ref={scrollerRef}>
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
                <Title>
                  Je donne {displayPrice(amount)}{" "}
                  {formData.paymentTimes === "M" && "par mois"}
                </Title>

                <Breadcrumb onClick={() => history.replace(amountStepUrl)} />
                <Spacer size="1rem" />

                <AmountInformations
                  group={group}
                  total={displayPrice(amount)}
                  amountGroup={displayPrice(groupAmount)}
                  amountNational={displayPrice(nationalAmount)}
                />

                <InformationsStep
                  formData={formData}
                  setFormData={setFormData}
                  errors={errors}
                  setErrors={setErrors}
                  isLoading={isLoading}
                  onSubmit={handleInformationsSubmit}
                  type={type}
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
