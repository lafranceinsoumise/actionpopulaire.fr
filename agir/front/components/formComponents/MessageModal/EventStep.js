import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import {
  FaComments,
  FaComment,
  FaBullhorn,
  FaExclamation,
  FaCalendar,
} from "@agir/front/genericComponents/FaIcon";

import * as style from "@agir/front/genericComponents/_variables.scss";
import { displayHumanDateString } from "@agir/lib/utils/time";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const EVENT_TYPE_ICONS = {
  G: FaComments,
  M: FaBullhorn,
  A: FaExclamation,
  O: FaCalendar,
  NULL: FaComment,
  default: FaCalendar,
};

const StyledOption = styled.button`
  width: 100%;
  display: flex;
  align-items: flex-start;
  border: none;
  margin: 0;
  text-decoration: none;
  background: inherit;
  cursor: pointer;
  text-align: left;
  -webkit-appearance: none;
  -moz-appearance: none;
  color: ${({ $loadMore }) => ($loadMore ? style.primary500 : style.black1000)};
  font-size: ${({ $loadMore }) => ($loadMore ? "0.875rem" : "1rem")};
  line-height: 1.2;
  padding: 0.5rem 0;

  &:last-child {
    margin-bottom: 0;
  }

  &:hover,
  &:focus {
    border: none;
    outline: none;
    background-color: ${({ $loadMore }) =>
      $loadMore ? "transparent" : style.black50};
    text-decoration: ${({ $loadMore }) => ($loadMore ? "underline" : "none")};
  }

  span {
    flex: 1 1 auto;
    margin: 0 0.75rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    strong,
    em {
      display: inline-block;
      text-overflow: ellipsis;
      overflow: hidden;
      max-width: 100%;
      white-space: nowrap;
      margin: 0;
      padding: 0;
    }

    strong {
      font-weight: 600;
      color: ${style.primary500};
    }

    em {
      font-weight: 400;
      color: ${style.black700};
      font-style: normal;

      &::first-letter {
        text-transform: uppercase;
      }

      &:empty {
        display: none;
      }
    }
  }

  ${RawFeatherIcon} {
    flex: 0 0 auto;
    margin: 0;
  }
`;

const StyledWarning = styled.p`
  display: flex;
  flex-flow: column nowrap;
  padding: 0 1rem;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0 1.5rem 1rem;
  border-left: 2px solid ${style.primary500};

  strong {
    font-weight: 600;
  }

  span + span {
    margin-top: 0.5rem;
  }
`;
const StyledWrapper = styled.div`
  max-height: 360px;
  overflow-x: hidden;
  overflow-y: auto;
  padding-top: 1.5rem;

  @media (max-width: ${style.collapse}px) {
    max-height: 100%;
  }

  & > *:last-child {
    margin-bottom: 1.5rem;
  }

  h4,
  ${StyledOption} {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  h4 {
    color: ${style.black1000};
    font-weight: 600;
    font-size: 1rem;
    line-height: 1.5;
    margin: 0 0 1rem;
  }
`;

const EventStepOption = (props) => {
  const { event, onSelect } = props;

  const handleClick = useCallback(() => {
    onSelect(event);
  }, [onSelect, event]);

  const Icon = useMemo(
    () =>
      (event.type && EVENT_TYPE_ICONS[event.type]) || EVENT_TYPE_ICONS.default,
    [event.type],
  );

  return (
    <StyledOption onClick={handleClick}>
      <Icon color={style.primary500} />
      <span>
        <strong>{event.name}</strong>
        <br />
        <em>
          {event.startTime ? displayHumanDateString(event.startTime) : null}
        </em>
      </span>
      <RawFeatherIcon name="chevron-right" color={style.primary500} />
    </StyledOption>
  );
};
EventStepOption.propTypes = {
  event: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string.isRequired,
    type: PropTypes.string,
    startTime: PropTypes.string,
  }).isRequired,
  onSelect: PropTypes.func.isRequired,
};

const EventStep = (props) => {
  const { events, onSelectEvent, loadMoreEvents, hasEmailWarning } = props;

  return (
    <StyledWrapper>
      <h4>Associer un événement au message&nbsp;?</h4>
      {hasEmailWarning && (
        <StyledWarning>
          <span>
            Les membres et abonné·es de votre groupe&nbsp;
            <strong>recevront un e-mail</strong> avec le contenu de votre
            message et <strong>pourront y répondre&nbsp;!</strong>
          </span>
          <span>
            (Il ne recevront pas d’e-mails pour chaque commentaire ou
            modification de messages)
          </span>
        </StyledWarning>
      )}
      {events.map((event, i) => (
        <EventStepOption
          key={event.id || i}
          event={event}
          onSelect={onSelectEvent}
        />
      ))}
      {typeof loadMoreEvents === "function" ? (
        <StyledOption $loadMore key="load-more" onClick={loadMoreEvents}>
          Voir plus
        </StyledOption>
      ) : null}
    </StyledWrapper>
  );
};
EventStep.propTypes = {
  events: PropTypes.arrayOf(PropTypes.object),
  onSelectEvent: PropTypes.func.isRequired,
  loadMoreEvents: PropTypes.func,
  hasEmailWarning: PropTypes.bool,
};
export default EventStep;
