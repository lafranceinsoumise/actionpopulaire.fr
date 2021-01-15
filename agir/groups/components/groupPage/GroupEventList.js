import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import EventCard from "@agir/front/genericComponents/EventCard";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledList = styled.div`
  padding-bottom: 1.5em;

  @media (max-width: ${style.collapse}px) {
    background: ${style.black25};
  }

  & > h3 {
    margin: 0;
    padding: 0 1rem 1.5rem;

    @media (max-width: ${style.collapse}px) {
      padding-top: 1.5rem;
    }

    &:empty {
      display: none;
    }
  }

  ${Card} {
    margin-bottom: 1rem;
  }

  & > ${Button} {
    &,
    &:hover,
    &:focus,
    &:active {
      background-color: transparent;
    }
    @media (min-width: ${style.collapse}px) {
      padding-left: 0;
      padding-right: 0;
    }
    @media (max-width: ${style.collapse}px) {
      width: 100%;
      justify-content: center;
    }
  }
`;
const GroupEventList = (props) => {
  const { title, events, isLoading, loadMore, loadMoreLabel } = props;

  const eventList = useMemo(
    () =>
      Array.isArray(events)
        ? events.map((event) => ({
            ...event,
            schedule: Interval.fromDateTimes(
              DateTime.fromISO(event.startTime).setLocale("fr"),
              DateTime.fromISO(event.endTime).setLocale("fr")
            ),
          }))
        : null,
    [events]
  );
  const isReady = Array.isArray(eventList);
  if (isReady && eventList.length === 0) {
    return null;
  }
  return (
    <StyledList style={{}}>
      <h3>
        {!!title && (
          <PageFadeIn
            ready={isReady}
            wait={
              <Skeleton
                boxes={1}
                style={{ width: "50%", height: "2em", margin: 0 }}
              />
            }
          >
            {title}
          </PageFadeIn>
        )}
      </h3>
      <PageFadeIn
        ready={isReady}
        wait={
          <Skeleton boxes={2} style={{ height: "150px", margin: "0 0 1rem" }} />
        }
      >
        {isReady &&
          eventList.map((event) => <EventCard key={event.id} {...event} />)}
      </PageFadeIn>
      {isReady && typeof loadMore === "function" ? (
        <Button color="white" onClick={loadMore} disabled={isLoading}>
          {loadMoreLabel ? (
            loadMoreLabel
          ) : (
            <>
              Charger plus d’événements&ensp;
              <RawFeatherIcon name="chevron-down" width="1em" strokeWidth={3} />
            </>
          )}
        </Button>
      ) : null}
    </StyledList>
  );
};
GroupEventList.propTypes = {
  title: PropTypes.string,
  events: PropTypes.arrayOf(PropTypes.object),
  isLoading: PropTypes.bool,
  loadMore: PropTypes.func,
  loadMoreLabel: PropTypes.string,
};
export default GroupEventList;
