import { Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import RenderIfVisible from "@agir/front/genericComponents/RenderIfVisible";
import styled from "styled-components";
import useSWR from "swr";

import EventCard from "@agir/front/genericComponents/EventCard";
import FilterTabs from "@agir/front/genericComponents/FilterTabs";
import Link from "@agir/front/app/Link";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import getMultiMeeting from "./multimeeting.hack";

import { dateFromISOString, displayHumanDay } from "@agir/lib/utils/time";

import { getAgendaEndpoint, useEventSuggestions } from "./api";

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

const EventSuggestions = ({ isPaused }) => {
  const { data: grandEvents } = useSWR(getAgendaEndpoint("grandEvents"), {
    revalidateIfStale: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });

  const [tabs, activeTab, setActiveTab, events] = useEventSuggestions(isPaused);

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

  const hackedGrandEvents = useMemo(() => {
    const events = Array.isArray(grandEvents) ? grandEvents : [];
    const multimeetingEvent = getMultiMeeting();
    if (!multimeetingEvent) {
      return events;
    }
    return [...events, multimeetingEvent].sort((a, b) =>
      a.startTime < b.startTime ? -1 : a.startTime > b.startTime ? 1 : 0
    );
  }, [grandEvents]);

  return (
    <>
      <FilterTabs
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      {/* GRAND EVENTS */}
      {activeTab === 0 && (
        <PageFadeIn ready={Array.isArray(grandEvents)} wait={<Skeleton />}>
          {hackedGrandEvents.length > 0 && (
            <div key={`${activeTab}__grand`}>
              <Day>Grands événements</Day>
              {hackedGrandEvents.map((event, i) => (
                <RenderIfVisible
                  key={`${activeTab}__${event.id}`}
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
      )}

      {/* ACTIVE TAB EVENTS */}
      <PageFadeIn ready={Array.isArray(events)} wait={<Skeleton />}>
        {Array.isArray(events) && events.length === 0 ? (
          <EmptyAgenda>
            {activeTab === 0 ? (
              <p>
                Zut ! Il n'y a pas d'événement prévu à proximité ?{" "}
                <Link route="personalInformation">
                  Vérifiez votre adresse et code postal
                </Link>
                .
              </p>
            ) : (
              <p>
                Pas d'événement {tabs[activeTab]} ?{" "}
                <Link route="createEvent">Commencez par en créer un</Link>.
              </p>
            )}
          </EmptyAgenda>
        ) : Array.isArray(events) ? (
          Object.entries(byDay).map(([date, events]) => (
            <div key={`${activeTab}__${date}`}>
              <Day>{date}</Day>
              {events.map((event, i) => (
                <RenderIfVisible
                  key={`${activeTab}__${event.id}`}
                  style={{ marginTop: i && "1rem" }}
                >
                  <EventCard {...event} />
                </RenderIfVisible>
              ))}
            </div>
          ))
        ) : null}
      </PageFadeIn>
    </>
  );
};
EventSuggestions.propTypes = {
  isPaused: PropTypes.func,
};
export default EventSuggestions;
