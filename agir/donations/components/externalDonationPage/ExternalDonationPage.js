import React, { useCallback, useEffect } from "react";
import Helmet from "react-helmet";
import { useHistory, useLocation, useParams } from "react-router-dom";

import { routeConfig } from "@agir/front/app/routes.config";
import { useDonations } from "@agir/donations/common/hooks";

import DonationForm from "@agir/donations/common/DonationForm";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import {
  StyledIllustration,
  StyledBody,
  StyledPage,
  StyledLogo,
  StyledMain,
  Theme,
} from "@agir/donations/common/StyledComponents";

const ExternalDonationPage = () => {
  const history = useHistory();
  const params = useParams();
  const { search, pathname } = useLocation();
  const urlParams = new URLSearchParams(search);

  const {
    config,
    formData,
    formErrors,
    sessionUser,
    isLoading,
    updateFormData,
    handleSubmit,
  } = useDonations(params?.type, {
    amount: urlParams.get("amount") || 0,
    paymentTimes: pathname.includes("dons-mensuels") ? "M" : "S",
  });

  const { allowedPaymentModes, beneficiary, externalLinkRoute, title, type } =
    config;
  const { paymentTimes } = formData;
  const paymentModes = allowedPaymentModes[paymentTimes];

  const handleBack = useCallback(
    () => history.replace(routeConfig.donations.getLink(params) + search),
    [history, params, search]
  );

  useEffect(() => {
    typeof sessionUser !== "undefined" && formData.amount === 0 && handleBack();
  }, [sessionUser, handleBack, formData.amount]);

  return (
    <Theme type={formData.to}>
      <Helmet>
        <title>{title}</title>
      </Helmet>

      <PageFadeIn
        ready={typeof sessionUser !== "undefined"}
        wait={<Skeleton />}
      >
        <StyledPage>
          <StyledIllustration aria-hidden="true" />
          <StyledBody>
            <StyledMain>
              <StyledLogo
                alt={`Logo ${beneficiary}`}
                route={externalLinkRoute}
                rel="noopener noreferrer"
                target="_blank"
              />
              <DonationForm
                isLoading={isLoading}
                type={type}
                formData={formData}
                formErrors={formErrors}
                allowedPaymentModes={paymentModes}
                hideEmailField={!!sessionUser?.email}
                updateFormData={updateFormData}
                onSubmit={handleSubmit}
                onBack={handleBack}
              />
              <Spacer size="2rem" />
            </StyledMain>
          </StyledBody>
        </StyledPage>
      </PageFadeIn>
    </Theme>
  );
};

export default ExternalDonationPage;
