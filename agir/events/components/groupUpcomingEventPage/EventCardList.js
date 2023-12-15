import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import MiniEventCard from "@agir/events/common/UpcomingEvents/MiniEventCard";

import { useEventsByDay } from "@agir/events/common/hooks";
import { simpleDate } from "@agir/lib/utils/time";

const StyledMiniEventCard = styled(MiniEventCard)`
  width: 100%;

  strong {
    font-size: 1rem;
  }
`;

const EventCardList = ({ events, isLoading, disabled, emptyText }) => {
  const eventsByDay = useEventsByDay(events, (date) => simpleDate(date, false));

  if (isLoading) {
    return null;
  }

  if (disabled) {
    return (
      <p>
        <em>
          Sélectionnez des groupes d’action pour pouvoir afficher la liste de
          leurs événements ici
        </em>
      </p>
    );
  }

  if (!Array.isArray(events) || events.length === 0) {
    return (
      <p>
        <em>
          {emptyText ||
            "Aucun événement à venir n'a été trouvé pour les groupes sélectionnés"}
        </em>
      </p>
    );
  }

  return Object.entries(eventsByDay).map(([date, events]) => (
    <React.Fragment key={date}>
      <h6>{date}</h6>
      {events.map((event) => (
        <StyledMiniEventCard key={event.id} {...event} />
      ))}
    </React.Fragment>
  ));
};

EventCardList.propTypes = {
  events: PropTypes.array,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
  emptyText: PropTypes.string,
};

export default EventCardList;
