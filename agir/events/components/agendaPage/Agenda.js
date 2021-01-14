import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { Row } from "@agir/donations/donationForm/AllocationsWidget/Styles";
import { Column } from "@agir/front/genericComponents/grid";
import Card from "@agir/front/genericComponents/Card";
import { LayoutTitle } from "@agir/front/dashboardComponents/Layout";
import Button from "@agir/front/genericComponents/Button";
import EventCard from "@agir/front/genericComponents/EventCard";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIs2022,
  getIsSessionLoaded,
  getRoutes,
  getUser,
} from "@agir/front/globalContext/reducers";

import { dateFromISOString, displayHumanDay } from "@agir/lib/utils/time";
import FilterTabs from "@agir/front/genericComponents/FilterTabs";
import Onboarding from "@agir/front/genericComponents/Onboarding";
import useSWR from "swr";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import logger from "@agir/lib/utils/logger";

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

    @media (max-width: ${style.collapse}px) {
      flex: 0 0 100%;
      margin-bottom: 1rem;
    }
  }

  & > div {
    display: flex;
    flex-direction: row-reverse;
    align-items: center;

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
    @media only screen and (max-width: ${style.collapse}px) {
      margin-left: 0.5rem;
    }
  }
`;

const Day = styled.h3`
  color: ${style.black500};
  text-transform: uppercase;
  font-size: 14px;
  margin-top: 24px;
`;

const EmptyAgenda = styled.div`
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
  & header {
    margin-bottom: 0;
  }

  & h2 {
    font-size: 18px;
    font-weight: 500;
  }

  & h2,
  & ${Day}, & ${EmptyAgenda} {
    margin: 2rem 0 1rem;

    @media (max-width: ${style.collapse}px) {
      margin: 2rem 25px 1rem;
    }
  }

  & ${Card} {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
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
          event.distance &&
          event.distance < 100 * 1000 &&
          !event.rsvp &&
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
      suggestions.map((event) => ({
        ...event,
        schedule: Interval.fromDateTimes(
          dateFromISOString(event.startTime),
          dateFromISOString(event.endTime)
        ),
      })),
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
              <a href={routes.createEvent}>Commencez par en créer un</a>.
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
  const is2022 = useSelector(getIs2022);
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  const { data: rsvped } = useSWR("/api/evenements/rsvped");
  const { data: suggestions } = useSWR("/api/evenements/suggestions");

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
        <TopBar>
          <LayoutTitle>Événements</LayoutTitle>
          <div>
            {routes.createEvent ? (
              <Button
                small
                as="a"
                color="secondary"
                href={routes["createEvent"]}
                icon="plus"
              >
                Créer un événement
              </Button>
            ) : null}
            {routes.eventMapPage ? (
              <Button small as="Link" route="eventMapPage" icon="map">
                Carte
              </Button>
            ) : null}
          </div>
        </TopBar>
      </header>
      <PageFadeIn ready={rsvpedEvents && suggestions} wait={<Skeleton />}>
        <Row style={{ marginBottom: "4rem" }}>
          <Column grow>
            {rsvpedEvents && rsvpedEvents.length > 0 && (
              <>
                <h2 style={{ marginTop: 0 }}>Mes événements</h2>
                {rsvpedEvents.map((event) => (
                  <EventCard key={event.id} {...event} />
                ))}
                <h2>Autres événements près de chez moi</h2>
              </>
            )}
            <PageFadeIn
              ready={isSessionLoaded && suggestions}
              wait={<Skeleton />}
            >
              {/* Suggested events are longer to load than rsvped,
              so when rsvpedEvents is loaded we still display skeleton
              only on this part */}
              <>
                {isSessionLoaded && suggestions && (
                  <SuggestionsEvents suggestions={suggestions} />
                )}
                <Row style={{ marginTop: "4rem" }}>
                  <Column grow>
                    <Onboarding
                      type={is2022 ? "group__nsp" : "group__action"}
                      routes={routes}
                    />
                  </Column>
                </Row>
                <Row style={{ marginTop: "4rem" }}>
                  <Column grow>
                    <Onboarding type="event" routes={routes} />
                  </Column>
                </Row>
              </>
            </PageFadeIn>
          </Column>
        </Row>
      </PageFadeIn>
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
