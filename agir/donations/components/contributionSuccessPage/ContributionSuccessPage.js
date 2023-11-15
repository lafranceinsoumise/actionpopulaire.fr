import React from "react";
import Helmet from "react-helmet";
import useSWRImmutable from "swr/immutable";

import CONFIG from "@agir/donations/common/config";
import { routeConfig } from "@agir/front/app/routes.config";

import {
  StyledBody,
  StyledIllustration,
  StyledLogo,
  StyledMain,
  StyledPage,
  Theme,
} from "@agir/donations/common/StyledComponents";
import Link from "@agir/front/app/Link";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import Button from "@agir/front/genericComponents/Button";

const TYPE = "contribution";

const ContributionSuccessPage = () => {
  const { data: session } = useSWRImmutable("/api/session/");

  const config = CONFIG[TYPE];
  const { beneficiary, externalLinkRoute, title, thankYouNote } = config;

  return (
    <Theme type={TYPE}>
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
                <h2>Merci pour votre contribution&nbsp;!</h2>
                <h4>
                  Vous allez recevoir un e-mail de confirmation dès que votre
                  paiement aura été validé.
                </h4>
                <p style={{ fontSize: "0.875rem" }}>
                  Vous pouvez à tout moment consulter vos dons et paiements
                  depuis l'onglet &laquo;&nbsp;Dons et paiements&nbsp;&raquo; de
                  votre espace personnel sur actionpopulaire.fr.
                </p>
                <Spacer size="1rem" />
                <p
                  css={`
                    text-align: center;
                  `}
                >
                  <Button
                    link
                    small
                    route="personalPayments"
                    icon="arrow-right"
                    color="secondary"
                  >
                    Aller sur la page &laquo;&nbsp;Dons et
                    paiements&nbsp;&raquo;
                  </Button>
                </p>
              </div>
              <Spacer size="2rem" />
              <div
                css={`
                  padding: 1rem;
                  background-color: ${({ theme }) => theme.black25};
                  border-radius: ${({ theme }) => theme.borderRadius};
                  font-size: 0.875rem;
                `}
              >
                {thankYouNote}
              </div>
              <Spacer size="3rem" />
              <ShareCard
                title="Encouragez vos ami·es à devenir financeur·euses:"
                url={routeConfig.contributions.getLink()}
              />
            </StyledMain>
          </StyledBody>
        </StyledPage>
      </PageFadeIn>
    </Theme>
  );
};

export default ContributionSuccessPage;
