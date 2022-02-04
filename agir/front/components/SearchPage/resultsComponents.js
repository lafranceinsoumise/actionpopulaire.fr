import PropTypes from "prop-types";
import React from "react";

import { Interval } from "luxon";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import EventCard from "@agir/front/genericComponents/EventCard";
import GroupSuggestionCard from "@agir/groups/groupPage/GroupSuggestionCard";
import { GroupSuggestionCarousel } from "@agir/groups/groupPage/GroupSuggestions";

const StackedGroupList = styled.div`
  display: flex;
  flex-flow: wrap;
  justify-content: space-between;
  gap: 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    justify-content: flex-start;
  }
  & > div {
    flex: 0 0 310px;
    margin-bottom: 10px;
    max-width: unset;
    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex: 1 1 310px;
    }
  }
`;

const CarrouselContainer = styled.div`
  margin-left: -12px;
  margin-right: -12px;
`;

export const GroupList = ({ groups, inline = false }) =>
  inline ? (
    <CarrouselContainer>
      <GroupSuggestionCarousel groups={groups} />
    </CarrouselContainer>
  ) : (
    <StackedGroupList>
      {groups?.map((group) => (
        <GroupSuggestionCard key={group.id} {...group} />
      ))}
    </StackedGroupList>
  );
GroupList.propTypes = {
  groups: PropTypes.array,
};

const EventItem = ({ event }) => (
  <>
    <EventCard {...event} />
    <Spacer size="1rem" />
  </>
);
EventItem.propTypes = {
  event: PropTypes.object,
};

export const EventList = ({ events }) => {
  const pastEvents = [];
  const futureEvents = [];
  events.map((event) => {
    event = {
      ...event,
      schedule: Interval.fromISO(`${event.startTime}/${event.endTime}`),
    };
    if (new Date() > new Date(event.endTime)) {
      pastEvents.push(event);
    } else {
      futureEvents.push(event);
    }
  });

  return (
    <>
      {!!futureEvents?.length && (
        <h3 style={{ textAlign: "right" }}>Evénements à venir</h3>
      )}
      {futureEvents.map((event) => (
        <EventItem key={event.id} event={event} />
      ))}

      {!!pastEvents?.length && (
        <h3 style={{ textAlign: "right" }}>Evénements passés</h3>
      )}
      {pastEvents.map((event) => (
        <EventItem key={event.id} event={event} />
      ))}
    </>
  );
};
EventList.propTypes = {
  events: PropTypes.array,
};

export const ListTitle = ({ name, list, onShowMore }) => (
  <h2>
    <div>
      {name} {list.length > 0 && <span>{list.length}</span>}
    </div>
    {onShowMore && (
      <Button color="primary" small onClick={onShowMore}>
        Voir tout
      </Button>
    )}
  </h2>
);

ListTitle.propTypes = {
  list: PropTypes.array,
  name: PropTypes.string,
  onShowMore: PropTypes.func,
};

export const NoResults = ({ name, list }) => {
  if (!Array.isArray(list) || !!list.length) {
    return null;
  }
  return (
    <>
      <Spacer size="1rem" />
      Aucun {name} n'est lié à cette recherche
    </>
  );
};
NoResults.propTypes = {
  list: PropTypes.array,
  name: PropTypes.string,
};
