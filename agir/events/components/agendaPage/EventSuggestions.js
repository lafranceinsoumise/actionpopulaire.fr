import RenderIfVisible from "@agir/front/genericComponents/RenderIfVisible";
import { Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";
import EventCard from "@agir/front/genericComponents/EventCard";
import FilterTabs from "@agir/front/genericComponents/FilterTabs";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import ActionRadiusField from "./ActionRadiusField";

import { dateFromISOString, displayHumanDay } from "@agir/lib/utils/time";
import { useEventSuggestions } from "./api";

const Bone = styled.div`
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.black50};
  margin-top: 1.5rem;
  height: 1.5rem;
  width: 30%;
  min-width: 160px;

  & + & {
    margin-top: 1rem;
    height: 148px;
    width: 100%;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      height: 272px;
    }
  }
`;

const EventSectionTitle = styled.h3`
  font-size: 1rem;
  line-height: 1.5;
  font-weight: 600;
  margin-top: 1.5rem;

  &::first-letter {
    text-transform: uppercase;
  }
`;

const EventGroupSectionTitle = styled(Link)`
  display: block;
  font-size: 0.75rem;
  line-height: 1.5;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: -1rem;
  text-transform: uppercase;
  color: ${(props) => props.theme.black500};

  &:hover,
  &:focus {
    text-decoration: none;
    color: ${(props) => props.theme.black500};
  }
`;

const EmptyAgenda = styled.div`
  padding: 1rem 0 0;

  p {
    strong {
      color: ${(props) => props.theme.black1000};
    }

    a {
      font-weight: 700;
      cursor: pointer;
    }
  }
`;

const Skeleton = () => (
  <>
    <Bone />
    <Bone />
    <Bone />
  </>
);

const useEventsByDay = (events) => {
  const byDay = useMemo(
    () =>
      Array.isArray(events)
        ? events.reduce((days, event) => {
            const day = displayHumanDay(dateFromISOString(event.startTime));
            (days[day] = days[day] || []).push({
              ...event,
              schedule: Interval.fromDateTimes(
                dateFromISOString(event.startTime),
                dateFromISOString(event.endTime)
              ),
            });
            return days;
          }, {})
        : undefined,
    [events]
  );

  return byDay;
};

const EventList = (props) => {
  const { events } = props;
  const byDay = useEventsByDay(events);

  return Array.isArray(events)
    ? Object.entries(byDay).map(([date, events]) => (
        <div key={date}>
          <EventSectionTitle>{date}</EventSectionTitle>
          {events.map((event, i) => (
            <RenderIfVisible key={event.id} style={{ marginTop: i && "1rem" }}>
              <EventCard {...event} />
            </RenderIfVisible>
          ))}
        </div>
      ))
    : null;
};

const GenericTab = (props) => {
  const { tabKey, tabEvents, activeTab } = props;

  const byDay = useEventsByDay(tabEvents);

  return (
    <PageFadeIn ready={Array.isArray(tabEvents)} wait={<Skeleton />}>
      {Array.isArray(tabEvents) && tabEvents.length === 0 ? (
        <EmptyAgenda>
          <p>
            Pas d'événement {activeTab} ?{" "}
            <Link route="createEvent">Commencez par en créer un</Link>.
          </p>
        </EmptyAgenda>
      ) : (
        <EventList events={tabEvents} />
      )}
    </PageFadeIn>
  );
};

const NearEventTab = (props) => {
  const { tabEvents } = props;

  return (
    <PageFadeIn ready={Array.isArray(tabEvents)} wait={<Skeleton />}>
      {Array.isArray(tabEvents) && tabEvents.length === 0 ? (
        <EmptyAgenda>
          <p>
            Zut ! Il n'y a pas d'événement prévu à proximité ?{" "}
            <Link route="personalInformation">
              Vérifiez votre adresse et code postal
            </Link>
            .
          </p>
        </EmptyAgenda>
      ) : (
        <EventList events={tabEvents} />
      )}
    </PageFadeIn>
  );
};

const GrandEvents = (props) => {
  const { events } = props;
  return (
    <PageFadeIn ready={Array.isArray(events)} wait={<Skeleton />}>
      {Array.isArray(events) && events.length > 0 && (
        <div key="grand-events">
          <EventSectionTitle>Grands événements</EventSectionTitle>
          {events.map((event, i) => (
            <RenderIfVisible
              key={`grand-events__${event.id}`}
              style={{ marginTop: i && "1rem" }}
            >
              <EventCard
                {...event}
                schedule={Interval.fromDateTimes(
                  dateFromISOString(event.startTime),
                  dateFromISOString(event.endTime)
                )}
              />
            </RenderIfVisible>
          ))}
        </div>
      )}
    </PageFadeIn>
  );
};

const GroupEventTab = (props) => {
  const { tabKey, tabEvents } = props;

  const [byGroup, groupNames] = useMemo(() => {
    if (!Array.isArray(tabEvents)) {
      return [];
    }
    const result = {};
    const groupNames = {};
    tabEvents.forEach((event) => {
      if (!Array.isArray(event.groups) || event.groups.length === 0) {
        return;
      }
      event.groups.forEach((group) => {
        groupNames[group.id] = group.name;
        result[group.id] = result[group.id] || [];
        result[group.id].push({
          ...event,
          schedule: Interval.fromDateTimes(
            dateFromISOString(event.startTime),
            dateFromISOString(event.endTime)
          ),
        });
      });
    });
    return [result, groupNames];
  }, [tabEvents]);

  return (
    <PageFadeIn ready={Array.isArray(tabEvents)} wait={<Skeleton />}>
      {Array.isArray(tabEvents) && tabEvents.length === 0 ? (
        <EmptyAgenda>
          <p>
            Pas d'événement dans vos groupes&nbsp;?{" "}
            <Link route="createEvent">Commencez par en créer un</Link>.
          </p>
        </EmptyAgenda>
      ) : Array.isArray(tabEvents) ? (
        Object.entries(byGroup).map(([groupPk, events]) => (
          <div key={`${tabKey}__${groupPk}`}>
            <EventGroupSectionTitle
              route="groupDetails"
              routeParams={{ groupPk, activeTab: "agenda" }}
              backLink="events"
            >
              {groupNames[groupPk]}
            </EventGroupSectionTitle>
            <EventList events={events} />
          </div>
        ))
      ) : null}
    </PageFadeIn>
  );
};

const TABS = {
  default: { Component: GenericTab },
  nearEvents: {
    Component: NearEventTab,
    hasActionRadius: true,
    hasGrandEvents: true,
  },
  groupEvents: { Component: GroupEventTab },
};

const EventSuggestions = ({ isPaused }) => {
  const [
    tabs,
    activeKey,
    activeTabIndex,
    setActiveTabIndex,
    events,
    grandEvents,
    actionRadiusRangeProps,
  ] = useEventSuggestions(isPaused);

  const activeTab = TABS[activeKey] || TABS.default;

  return (
    <>
      <FilterTabs
        tabs={tabs}
        activeTab={activeTabIndex}
        onTabChange={setActiveTabIndex}
      />
      {activeTab.hasActionRadius && (
        <ActionRadiusField {...actionRadiusRangeProps} />
      )}
      {activeTab.hasGrandEvents && <GrandEvents events={grandEvents} />}
      <activeTab.Component
        activeTab={tabs[activeTabIndex]}
        tabKey={activeKey}
        tabEvents={events}
      />
    </>
  );
};
EventSuggestions.propTypes = {
  isPaused: PropTypes.func,
};
export default EventSuggestions;
