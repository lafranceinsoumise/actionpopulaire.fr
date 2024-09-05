import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import EventCard from "@agir/front/genericComponents/EventCard";

const StyledList = styled.div`
  padding-bottom: 1.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    background: ${(props) => props.theme.text25};
    padding-bottom: ${({ $length }) => ($length === 1 ? "0" : "1.5rem")};
  }

  & > h3 {
    margin: 0;
    padding: 0 0 1.5rem 0;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      padding: 1.5rem 1rem;
    }

    &:empty {
      display: none;
    }
  }

  ${Card} + ${Card} {
    margin-top: 1rem;
  }

  & > ${Button} {
    @media (max-width: ${(props) => props.theme.collapse}px) {
      width: 100%;
    }
  }
`;
const GroupEventList = (props) => {
  const { title, events, isLoading, loadMore, loadMoreLabel } = props;

  const eventList = useMemo(
    () =>
      Array.isArray(events)
        ? events.map((event) =>
            event
              ? {
                  ...event,
                  schedule: Interval.fromDateTimes(
                    DateTime.fromISO(event.startTime).setLocale("fr"),
                    DateTime.fromISO(event.endTime).setLocale("fr"),
                  ),
                }
              : null,
          )
        : null,
    [events],
  );
  const isReady = Array.isArray(eventList);
  if (isReady && eventList.length === 0) {
    return null;
  }
  return (
    <StyledList $length={(eventList && eventList.length) || 0}>
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
        <Button
          color="link"
          onClick={loadMore}
          disabled={isLoading}
          icon="chevron-down"
          rightIcon
        >
          {loadMoreLabel || "Charger plus d’événements"}
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
