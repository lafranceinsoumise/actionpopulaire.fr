import { DateTime, Interval } from "luxon";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import ActionButtons from "@agir/front/app/ActionButtons/ActionButtons";
import { LayoutTitle } from "@agir/front/app/Layout/StyledComponents";
import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import RenderIfVisibile from "@agir/front/genericComponents/RenderIfVisible";
import { Hide, useIsDesktop } from "@agir/front/genericComponents/grid";

import UpcomingEvents from "@agir/events/common/UpcomingEvents";
import Onboarding from "@agir/front/genericComponents/Onboarding";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import EventSuggestions from "./EventSuggestions";

import DonationAnnouncement from "@agir/activity/announcements/DonationAnnouncement";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getRoutes,
  getUser,
} from "@agir/front/globalContext/reducers";
import logger from "@agir/lib/utils/logger";
import { getAgendaEndpoint } from "./api.js";

const log = logger(__filename);

const TopBar = styled.div`
  display: flex;
  flex-flow: row wrap;
  justify-content: space-between;
  margin: 0 0 25px;

  @media (max-width: ${style.collapse}px) {
    margin: 0 0 2rem;
  }

  & > ${LayoutTitle} {
    margin: 0;
  }

  & > div {
    display: flex;
    flex-direction: row-reverse;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;

    @media only screen and (max-width: ${style.collapse}px) {
      flex-direction: row;
      margin-left: 1.5rem;
      margin-right: 1.5rem;
    }
  }

  & ${Button} + ${Button} {
    @media only screen and (min-width: ${style.collapse}px) {
      margin-right: 0.5rem;
    }
  }
`;

const StyledAgenda = styled.div`
  @media (max-width: ${(props) => props.theme.collapse}px) {
    background-color: ${(props) => props.theme.black25};
    box-sizing: border-box;
    padding: 1rem;
  }

  & h2 {
    font-size: 1.125rem;
    font-weight: 500;
  }

  & ${Card} + ${Card} {
    margin-top: 1rem;
  }
`;

const Agenda = () => {
  const routes = useSelector(getRoutes);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const user = useSelector(getUser);
  const isDesktop = useIsDesktop();

  const isPaused = useCallback(() => {
    return !user;
  }, [user]);

  const { data: rsvped } = useSWR(
    !isDesktop && getAgendaEndpoint("rsvpedEvents"),
    {
      isPaused,
    },
  );
  log.debug("Rsvped events ", rsvped);

  const rsvpedEvents = useMemo(
    () =>
      Array.isArray(rsvped)
        ? rsvped.map((event) => ({
            ...event,
            schedule: Interval.fromDateTimes(
              DateTime.fromISO(event.startTime).setLocale("fr"),
              DateTime.fromISO(event.endTime).setLocale("fr"),
            ),
          }))
        : [],
    [rsvped],
  );

  const isReady = isSessionLoaded && (isDesktop || !!rsvped);

  return (
    <StyledAgenda>
      <header>
        <Hide $over>
          <h2
            style={{
              textAlign: "center",
              fontWeight: 600,
              fontSize: "1.25rem",
              marginBottom: "1.5rem",
              marginTop: 0,
            }}
          >
            Bonjour{" "}
            {user?.displayName?.length > 2
              ? user?.displayName
              : user?.firstName || user?.displayName}{" "}
            👋
          </h2>
          <ActionButtons />
        </Hide>
        <Hide as={Spacer} $over size="1.5rem" />
        <DonationAnnouncement />
        <Hide as={Spacer} $under size="1.5rem" />
        <TopBar>
          <LayoutTitle>
            Bonjour{" "}
            {user?.displayName && user?.displayName.length > 2
              ? user.displayName
              : user?.firstName || user?.displayName}{" "}
            👋
          </LayoutTitle>
          <Hide as="nav" $under>
            <Button
              small
              link
              route="groupUpcomingEvents"
              icon="calendar"
              color="transparent"
            >
              Agenda des GA
            </Button>
            &ensp;
            <Button small link route="eventMap" icon="map">
              Carte
            </Button>
          </Hide>
        </TopBar>
      </header>
      <PageFadeIn
        style={{ marginBottom: "4rem" }}
        ready={isReady}
        wait={<Skeleton />}
      >
        {rsvpedEvents && rsvpedEvents.length > 0 ? (
          <Hide $over style={{ padding: "0 0 2rem" }}>
            <h2
              style={{
                fontWeight: 600,
                fontSize: "1.125rem",
                margin: "0 0 0.5rem",
                lineHeight: 1.4,
              }}
            >
              Mes événements prévus
            </h2>
            <UpcomingEvents events={rsvpedEvents} />
          </Hide>
        ) : null}
        <Hide
          $over
          style={{
            display: "flex",
            alignItems: "center",
            padding: "0 0 1rem",
          }}
        >
          <h2
            style={{
              fontWeight: 600,
              fontSize: "1.125rem",
              margin: 0,
              flex: "1 1 auto",
            }}
          >
            Événements
          </h2>
          <Button
            small
            link
            route="groupUpcomingEvents"
            icon="calendar"
            color="transparent"
          >
            Agenda des GA
          </Button>
          &ensp;
          <Button small link route="eventMap" icon="map">
            Carte
          </Button>
        </Hide>
        <EventSuggestions isPaused={isPaused} />
        <Spacer size="4rem" />
        <RenderIfVisibile once>
          <Onboarding type="group__action" routes={routes} />
          <Spacer size="4rem" />
          <Onboarding type="event" routes={routes} />
          <Spacer size="4rem" />
        </RenderIfVisibile>
      </PageFadeIn>
      <FeedbackButton />
    </StyledAgenda>
  );
};
export default Agenda;
