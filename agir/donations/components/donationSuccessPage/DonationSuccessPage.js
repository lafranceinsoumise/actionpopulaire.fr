import React from "react";
import Helmet from "react-helmet";
import { useParams } from "react-router-dom";
import useSWR from "swr";

import CONFIG from "@agir/donations/common/config";
import { MANUAL_REVALIDATION_SWR_CONFIG } from "@agir/front/allPages/SWRContext";
import { routeConfig } from "@agir/front/app/routes.config";

import {
  StyledBody,
  StyledIllustration,
  StyledLogo,
  StyledMain,
  StyledPage,
  Theme,
} from "@agir/donations/common/StyledComponents";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

const DonationPage = () => {
  const { data: session } = useSWR(
    "/api/session/",
    MANUAL_REVALIDATION_SWR_CONFIG
  );

  const params = useParams();
  const type =
    params?.type && CONFIG[type] ? params?.type : CONFIG.default.type;
  const config = CONFIG[type];
  const { beneficiary, externalLinkRoute, title, thankYouNote } = config;

  return (
    <Theme type={type}>
      <Helmet>
        <title>{title}</title>
      </Helmet>
      <PageFadeIn ready={typeof session !== "undefined"} wait={<Skeleton />}>
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
              <Spacer size="2rem" />
              <div>
                <h2>Merci pour votre don&nbsp;!</h2>
                <h4>
                  Vous allez recevoir un e-mail de confirmation dès que votre
                  paiement aura été validé.
                </h4>
              </div>
              <Spacer size="2rem" />
              {thankYouNote}
              <Spacer size="3rem" />
              <ShareCard
                title="Encouragez vos ami·es à faire un don :"
                url={routeConfig.donations.getLink({
                  type: params?.type,
                })}
              />
            </StyledMain>
          </StyledBody>
        </StyledPage>
      </PageFadeIn>
    </Theme>
  );
};

export default DonationPage;
