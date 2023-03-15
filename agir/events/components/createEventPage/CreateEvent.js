import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";

import TokTokCard from "@agir/events/TokTok/TokTokCard";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { Container, Hide } from "@agir/front/genericComponents/grid";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import EventForm from "./EventForm";

import BackLink from "@agir/front/app/Navigation/BackLink";
import illustration from "./images/team-spirit.svg";

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

const CreateEvent = () => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  return (
    <PageFadeIn wait={<CreateEventSkeleton />} ready={isSessionLoaded}>
      <StyledContainer>
        <div>
          <BackLink style={{ margin: 0 }}>
            <RawFeatherIcon name="arrow-left" color={style.black1000} />
          </BackLink>
          <Spacer size="1.5rem" />
          <h2>Nouvel événement</h2>
          <InfoBlock over />
          <Spacer size="1.5rem" />
          <EventForm />
        </div>
        <div>
          <InfoBlock under />
        </div>
      </StyledContainer>
    </PageFadeIn>
  );
};

export default CreateEvent;
