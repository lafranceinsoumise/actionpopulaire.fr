import PropTypes from "prop-types";
import React, { useCallback, useRef } from "react";
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

const StyledCard = styled(Card)`
  min-height: 25rem;
  min-width: 20rem;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  gap: 1rem;
  opacity: ${(props) => (props.$disabled ? 0.7 : 1)};
  cursor: ${(props) => (props.$disabled ? "not-allowed" : "pointer")};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    min-height: 14rem;
    min-width: unset;
  }

  &,
  &:hover,
  &:focus {
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
`;

const StyledCards = styled.div`
  display: flex;
  flex-direction: row;
  gap: 1.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: column;
  }

  ${Card} {
    flex: 1 1 50%;
  }
`;

const DonationLandingPageCard = (props) => {
  const { title, children, route, linkLabel, disabled } = props;
  const linkRef = useRef();
  const handleClick = useCallback(
    (e) => {
      e.preventDefault();
      !disabled && linkRef.current && linkRef.current.click();
    },
    [disabled],
  );

  return (
    <StyledCard $disabled={disabled} onClick={handleClick}>
      <h5>{title}</h5>
      {children}
      <Button
        ref={linkRef}
        color={disabled ? "success" : "secondary"}
        link={!disabled}
        backLink="donationLanding"
        route={route}
        disabled={disabled}
        small
        wrap
      >
        {linkLabel}
      </Button>
    </StyledCard>
  );
};

DonationLandingPageCard.propTypes = {
  title: PropTypes.node,
  children: PropTypes.node,
  route: PropTypes.string,
  linkLabel: PropTypes.string,
  disabled: PropTypes.bool,
};

const DonationLandingPage = () => {
  const { data: session, isLoading } = useSWRImmutable("/api/session/");

  const user = session?.user;
  const config = CONFIG.default;
  const hasContribution =
    !!user?.activeContribution && !user.activeContribution.renewable;

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
                <DonationLandingPageCard
                  title="Don ponctuel"
                  route="donations"
                  linkLabel="Je fais un don ponctuel"
                >
                  <p>
                    Chaque don nous aide à l’organisation d’événements, à
                    l’achat de matériel, au fonctionnement de ce site, etc. Nous
                    avons besoin du soutien financier de chacun·e d’entre vous.
                  </p>
                </DonationLandingPageCard>
                <DonationLandingPageCard
                  title="Devenir financeur·euse"
                  route="contributions"
                  linkLabel={
                    hasContribution
                      ? "Vous avez déjà validé votre contibution !"
                      : "Je deviens financeur·euse"
                  }
                  disabled={hasContribution}
                >
                  <p>
                    La contribution volontaire est un don{" "}
                    <strong>versé mensuellement</strong> jusqu’à la fin de
                    l’année civile. En devenant financeur·euse de la France
                    insoumise, vous vous engagez à ce que votre contribution
                    soit versée chaque mois jusqu’au mois de décembre.
                  </p>
                </DonationLandingPageCard>
              </StyledCards>
            </StyledMain>
          </StyledBody>
        </StyledPage>
      </PageFadeIn>
    </Theme>
  );
};

export default DonationLandingPage;
