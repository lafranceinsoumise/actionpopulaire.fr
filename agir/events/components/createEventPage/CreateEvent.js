import React, { useMemo } from "react";
import { Redirect } from "react-router-dom";
import { DateTime } from "luxon";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getBackLink,
} from "@agir/front/globalContext/reducers";
import { useMissingRequiredEventDocuments } from "@agir/events/common/hooks";
import { routeConfig } from "@agir/front/app/routes.config";

import Link from "@agir/front/app/Link";
import { Container, Hide } from "@agir/front/genericComponents/grid";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import TokTokCard from "@agir/events/TokTok/TokTokCard";
import StaticToast from "@agir/front/genericComponents/StaticToast";

import EventForm from "./EventForm";

import illustration from "./images/team-spirit.svg";

const IndexLinkAnchor = styled(Link)`
  font-weight: 600;
  font-size: 12px;
  line-height: 1.4;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const Illustration = styled.div`
  width: 100%;
  height: 260px;
  background-repeat: no-repeat;
  background-size: contain;
  background-position: center center;
  background-image: url(${illustration});
`;

const StyledInfoBlock = styled(Hide)`
  margin: 0;
  padding: 0;

  & > * {
    margin: 0;
    padding: 0;
    font-size: 1rem;
    line-height: 1.5;
    font-weight: 400;
  }

  & > h3 {
    font-weight: 700;
  }

  ${Illustration} {
    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }
`;

const StyledContainer = styled(Container)`
  margin: 4rem auto;
  margin-top: 2rem;
  padding: 0;
  background-color: white;
  width: 100%;
  max-width: 1098px;
  display: grid;
  grid-template-columns: 1fr 300px;
  grid-gap: 1.5rem;

  @media (max-width: ${style.collapse}px) {
    margin: 0;
    display: block;
  }

  & > div {
    padding: 0 1.5rem;
  }

  & > div + div {
    padding: 0;

    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }

  h2 {
    font-size: 26px;
    font-weight: 700;
    margin: 0;
  }
`;

const CreateEventSkeleton = () => (
  <StyledContainer>
    <div>
      <Skeleton boxes={5} />
    </div>
    <div width="348px">
      <Skeleton boxes={2} />
    </div>
  </StyledContainer>
);

const InfoBlock = (props) => (
  <StyledInfoBlock {...props}>
    <Illustration aria-hidden="true" />
    <Spacer size="1rem" />
    <p>
      En publiant votre événement, ce dernier sera visible à toutes les
      personnes aux alentours.
      <Spacer size="0.5rem" />
      <Link route="newGroupHelp" target="_blank" rel="noopener noreferrer">
        Besoin d'idées d'événements&nbsp;?
      </Link>
      <Spacer size="0.5rem" />
      <Link route="help" target="_blank" rel="noopener noreferrer">
        Consulter le centre d'aide
      </Link>
    </p>
    <Hide under>
      <Spacer size="1.5rem" />
      <TokTokCard />
    </Hide>
  </StyledInfoBlock>
);

export const ToastElectionInfo = () => (
  <StaticToast $color={style.primary500} style={{ marginTop: "1rem" }}>
    Trève électorale : la veille d'une élection, la loi vous interdit de faire
    campagne. Vous ne pouvez pas organiser d'action en but de récolter des
    suffrages (porte-à-porte, tractage, réunion publique...). Seuls les
    événements internes à la campagne sont autorisés.
  </StaticToast>
);

const CreateEvent = () => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);

  const now = DateTime.local();

  const NO_CREATION_DATES = {
    start: DateTime.fromISO("2022-04-09"),
    end: DateTime.fromISO("2022-04-10").plus({ hours: 20 }),
  };

  // Forbid event creation during election
  if (now > NO_CREATION_DATES.start && now < NO_CREATION_DATES.end) {
    return <Redirect to={routeConfig.treveCreationPage.getLink()} />;
  }

  const { projects } = useMissingRequiredEventDocuments();

  const isBlocked = useMemo(() => {
    if (!Array.isArray(projects) || projects.length === 0) {
      return false;
    }
    return projects.some((project) => project.isBlocking);
  }, [projects]);

  return (
    <PageFadeIn
      wait={<CreateEventSkeleton />}
      ready={isSessionLoaded && typeof projects !== "undefined"}
    >
      {isBlocked ? (
        <Redirect to={routeConfig.missingEventDocuments.getLink()} />
      ) : (
        <StyledContainer>
          <div>
            {!!backLink && (
              <IndexLinkAnchor
                to={backLink.to}
                href={backLink.href}
                route={backLink.route}
                aria-label={backLink.label || "Retour à l'accueil"}
                title={backLink.label || "Retour à l'accueil"}
              >
                <RawFeatherIcon name="arrow-left" color={style.black1000} />
              </IndexLinkAnchor>
            )}
            <Spacer size="1.5rem" />
            <h2>Nouvel événement</h2>
            <ToastElectionInfo />
            <InfoBlock over />
            <Spacer size="1.5rem" />
            <EventForm />
          </div>
          <div>
            <InfoBlock under />
          </div>
        </StyledContainer>
      )}
    </PageFadeIn>
  );
};

export default CreateEvent;
