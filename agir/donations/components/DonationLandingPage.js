import React from "react";
import styled from "styled-components";
import useSWRImmutable from "swr/immutable";

import CONFIG from "@agir/donations/common/config";

import {
  StyledBody,
  StyledIllustration,
  StyledLogo,
  StyledMain,
  StyledPage,
  Theme,
} from "@agir/donations/common/StyledComponents";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Link from "@agir/front/app/Link";
import Spacer from "@agir/front/genericComponents/Spacer";
import Card from "@agir/front/genericComponents/Card";
import Button from "@agir/front/genericComponents/Button";

const StyledCards = styled.div`
  display: flex;
  flex-direction: row;
  gap: 1.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: column;
  }

  ${Card} {
    min-height: 25rem;
    min-width: 20rem;
    flex: 1 1 50%;
    display: flex;
    flex-direction: column;
    padding: 1.5rem;
    gap: 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      min-height: 14rem;
      min-width: unset;
      border-radius: ${(props) => props.theme.borderRadius};
      border: 1px solid ${(props) => props.theme.black500};
      box-shadow: none;
    }

    & > * {
      margin: 0;
    }

    h5 {
      font-size: 1.125rem;
      font-weight: 600;
    }

    ${Button} {
      margin-top: auto;
      align-self: center;
    }
  }
`;

const DonationPage = () => {
  const { data: session, isLoading } = useSWRImmutable("/api/session/");

  const config = CONFIG.default;

  return (
    <Theme type={config.type}>
      <PageFadeIn ready={!isLoading} wait={<Skeleton />}>
        <StyledPage>
          <StyledIllustration aria-hidden="true" />
          <StyledBody>
            <StyledMain style={{ paddingBottom: "4rem" }}>
              <StyledLogo
                alt={`Logo ${config.beneficiary}`}
                route={config.externalLinkRoute}
                rel="noopener noreferrer"
                target="_blank"
              />
              <h2>Financer les actions du mouvement</h2>
              <Spacer size="1rem" />
              <p>
                En devenant financeur·euse, le groupes d’action ont plus de
                visibilité pour financer leurs actions.
              </p>
              <p>
                <Link route="donationHelp">En savoir plus</Link>
              </p>
              <Spacer size="1.5rem" />
              <StyledCards>
                <Card>
                  <h5>Don ponctuel</h5>
                  <p>
                    Chaque don nous aide à l’organisation d’événements, à
                    l’achat de matériel, au fonctionnement de ce site, etc. Nous
                    avons besoin du soutien financier de chacun·e d’entre vous.
                  </p>
                  <Button link small route="donations" color="secondary">
                    Je fais un don ponctuel
                  </Button>
                </Card>
                <Card>
                  <h5>Devenir financeur·euse</h5>
                  <p>
                    La contribution volontaire est un don{" "}
                    <strong>versé mensuellement</strong> jusqu’à la fin de
                    l’année civile. En devenant financeur·euse de la France
                    insoumise, vous vous engagez à ce que votre contribution
                    soit versée chaque mois jusqu’au mois de décembre.
                  </p>
                  <Button link small route="contributions" color="secondary">
                    Je deviens financeur·euse
                  </Button>
                </Card>
              </StyledCards>
            </StyledMain>
          </StyledBody>
        </StyledPage>
      </PageFadeIn>
    </Theme>
  );
};

export default DonationPage;
