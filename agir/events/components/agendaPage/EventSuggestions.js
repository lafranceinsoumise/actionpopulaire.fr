import { Interval } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import EventCard from "@agir/front/genericComponents/EventCard";
import FilterTabs from "@agir/front/genericComponents/FilterTabs";
import Link from "@agir/front/app/Link";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import { dateFromISOString, displayHumanDay } from "@agir/lib/utils/time";

import { EVENT_TYPES, useEventSuggestions } from "./api";

const Box = styled.div`
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

const EventSuggestions = ({ isPaused }) => {
  const [tabs, activeTab, setActiveTab, events] = useEventSuggestions(isPaused);

  const byDay = React.useMemo(
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
        : events,
    [events]
  );

  return (
    <>
      <FilterTabs tabs={tabs} onTabChange={setActiveTab} />
      <PageFadeIn
        ready={Array.isArray(events)}
        wait={
          <>
            <Box />
            <Box />
            <Box />
          </>
        }
      >
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
              {events.map((event) => (
                <EventCard key={`${activeTab}__${event.id}`} {...event} />
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
