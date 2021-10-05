import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import ActionButtons from "@agir/front/app/ActionButtons";
import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import EventCard from "@agir/front/genericComponents/EventCard";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import FilterTabs from "@agir/front/genericComponents/FilterTabs";
import { Hide } from "@agir/front/genericComponents/grid";
import { LayoutTitle } from "@agir/front/dashboardComponents/Layout/StyledComponents";
import Link from "@agir/front/app/Link";
import MissingDocumentsWidget from "@agir/events/eventRequiredDocuments/MissingDocuments/MissingDocumentsWidget";
import Onboarding from "@agir/front/genericComponents/Onboarding";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import UpcomingEvents from "@agir/events/common/UpcomingEvents";

import { dateFromISOString, displayHumanDay } from "@agir/lib/utils/time";
import {
  getIsSessionLoaded,
  getRoutes,
  getUser,
} from "@agir/front/globalContext/reducers";
import logger from "@agir/lib/utils/logger";
import { useSelector } from "@agir/front/globalContext/GlobalContext";

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

const Day = styled.h3`
  font-size: 1rem;
  line-height: 1.5;
  font-weight: 600;
  margin-top: 24px;

  &::first-letter {
    text-transform: uppercase;
  }
`;

const EmptyAgenda = styled.div`
  padding: 1rem 0 0;

  & p {
    strong {
      color: ${style.black1000};
    }
    a {
      font-weight: bold;
      cursor: pointer;
    }
  }
`;

const StyledAgenda = styled.div`
  @media (max-width: ${(props) => props.theme.collapse}px) {
    box-sizing: border-box;
    padding: 0 1rem;
  }

  & h2 {
    font-size: 1.125rem;
    font-weight: 500;
  }

  & ${Card} + ${Card} {
    margin-top: 1rem;
  }
`;

const otherEventConfig = {
  NEAR_TYPE: {
    label: "À proximité",
    allowEmpty: true,
    filter: (events) =>
      events.filter(
        (event) =>
          typeof event.distance === "number" &&
          event.distance < 100 * 1000 &&
          dateFromISOString(event.endTime) > DateTime.local()
      ),
  },
  GROUPS_TYPE: {
    label: "Dans mes groupes",
    allowEmpty: (user) =>
      user && Array.isArray(user.groups) && user.groups.length > 0,
    filter: (events) =>
      events.filter(
        (event) =>
          Array.isArray(event.groups) &&
          dateFromISOString(event.endTime) > DateTime.local() &&
          event.groups.some((group) => !!group.isMember)
      ),
  },
  PENDING_TYPE: {
    label: "En cours",
    allowEmpty: false,
    filter: (events) =>
      events
        .filter(
          (event) =>
            dateFromISOString(event.startTime) <= DateTime.local() &&
            dateFromISOString(event.endTime) >= DateTime.local()
        )
        .reverse(),
  },
  PAST_TYPE: {
    label: "Passés",
    allowEmpty: false,
    filter: (events) =>
      events
        .filter((event) => dateFromISOString(event.endTime) < DateTime.local())
        .reverse(),
  },
  ORGANIZED_TYPE: {
    label: "Organisés",
    allowEmpty: false,
    filter: (events) => events.filter((event) => event.isOrganizer).reverse(),
  },
};

const SuggestionsEvents = ({ suggestions }) => {
  log.debug("Suggested events ", suggestions);
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);

  const events = React.useMemo(
    () =>
      Array.isArray(suggestions)
        ? suggestions.map((event) => ({
            ...event,
            schedule: Interval.fromDateTimes(
              dateFromISOString(event.startTime),
              dateFromISOString(event.endTime)
            ),
          }))
        : [],
    [suggestions]
  );
  const byType = React.useMemo(
    () =>
      Object.entries(otherEventConfig).reduce(
        (result, [typeKey, typeConfig]) => ({
          ...result,
          [typeKey]: typeConfig.filter(events),
        }),
        {}
      ),
    [events]
  );
  const types = React.useMemo(
    () =>
      Object.keys(byType).filter((type) => {
        if (byType[type].length > 0) {
          return true;
        }
        if (typeof otherEventConfig[type].allowEmpty === "function") {
          return otherEventConfig[type].allowEmpty(user);
        }
        return otherEventConfig[type].allowEmpty;
      }),
    [byType, user]
  );
  const tabs = React.useMemo(
    () => types.map((type) => otherEventConfig[type].label),
    [types]
  );

  const [activeType, setActiveType] = React.useState(types[0]);
  const updateFilter = React.useCallback(
    (i) => {
      setActiveType(types[i] || types[0]);
    },
    [types]
  );

  const activeTypeEvents = React.useMemo(
    () =>
      Object.entries(
        byType[activeType]
          ? byType[activeType].reduce((days, event) => {
              const day = displayHumanDay(dateFromISOString(event.startTime));
              (days[day] = days[day] || []).push(event);
              return days;
            }, {})
          : {}
      ),
    [byType, activeType]
  );

  return (
    <>
      <FilterTabs tabs={tabs} onTabChange={updateFilter} />
      {activeTypeEvents.length === 0 ? (
        <EmptyAgenda>
          {activeType === "NEAR_TYPE" && routes.personalInformation ? (
            <p>
              Zut ! Il n'y a pas d'événement prévu à proximité ?{" "}
              <a href={routes.personalInformation}>
                Vérifiez votre adresse et code postal
              </a>
              .
            </p>
          ) : (
            <p>
              Pas d'événement prévu dans votre ville ?{" "}
              <Link route="createEvent">Commencez par en créer un</Link>.
            </p>
          )}
        </EmptyAgenda>
      ) : (
        activeTypeEvents.map(([date, events]) => (
          <div key={date}>
            <Day>{date}</Day>
            {events.map((event) => (
              <EventCard key={event.id} {...event} />
            ))}
          </div>
        ))
      )}
    </>
  );
};

SuggestionsEvents.propTypes = {
  suggestions: PropTypes.arrayOf(PropTypes.object),
};

const Agenda = () => {
  const routes = useSelector(getRoutes);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const user = useSelector(getUser);

  const isPaused = useCallback(() => {
    return !user;
  }, [user]);

  const { data: rsvped } = useSWR("/api/evenements/rsvped/", {
    isPaused,
  });

  const { data: suggestions } = useSWR("/api/evenements/suggestions/", {
    isPaused,
  });

  const rsvpedEvents = React.useMemo(
    () =>
      Array.isArray(rsvped)
        ? rsvped.map((event) => ({
            ...event,
            schedule: Interval.fromDateTimes(
              DateTime.fromISO(event.startTime).setLocale("fr"),
              DateTime.fromISO(event.endTime).setLocale("fr")
            ),
          }))
        : [],
    [rsvped]
  );

  return (
    <StyledAgenda>
      <header>
        <Hide over>
          <h2
            style={{
              textAlign: "center",
              fontWeight: 600,
              fontSize: "1.25rem",
              marginBottom: "1.5rem",
              marginTop: 0,
            }}
          >
            Bonjour {user?.firstName || user?.displayName} 👋
          </h2>
          <ActionButtons />
        </Hide>
        <TopBar>
          <LayoutTitle>
            Bonjour {user?.firstName || user?.displayName} 👋
          </LayoutTitle>
          <Hide under>
            <Button small link route="eventMap" icon="map">
              Carte
            </Button>
          </Hide>
        </TopBar>
      </header>
      <MissingDocumentsWidget />
      <PageFadeIn
        style={{ marginBottom: "4rem" }}
        ready={rsvpedEvents && suggestions}
        wait={<Skeleton />}
      >
        {rsvpedEvents && rsvpedEvents.length > 0 ? (
          <Hide over style={{ padding: "0 0 2rem" }}>
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
          over
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
          <Button small link route="eventMap" icon="map">
            Carte
          </Button>
        </Hide>
        <PageFadeIn ready={isSessionLoaded && suggestions} wait={<Skeleton />}>
          {isSessionLoaded && suggestions && (
            <SuggestionsEvents suggestions={suggestions} />
          )}
          <Spacer size="4rem" />
          <Onboarding type="group__action" routes={routes} />
          <Spacer size="4rem" />
          <Onboarding type="event" routes={routes} />
          <Spacer size="4rem" />
        </PageFadeIn>
      </PageFadeIn>
      <FeedbackButton />
    </StyledAgenda>
  );
};
export default Agenda;

Agenda.propTypes = {
  rsvped: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      startTime: PropTypes.string,
      endTime: PropTypes.string,
    })
  ),
  suggestions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      startTime: PropTypes.string,
      endTime: PropTypes.string,
    })
  ),
};
