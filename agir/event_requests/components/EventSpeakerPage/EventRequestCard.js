/* eslint-disable react/no-unknown-property */
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { simpleDateTime } from "@agir/lib/utils/time";

import Card from "@agir/front/genericComponents/Card";
import CheckboxField from "@agir/front/formComponents/CheckboxField";

import EventSpeakerRequestForm from "./EventSpeakerRequestForm";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledCard = styled(Card)`
  border-radius: ${(props) => props.theme.borderRadius};
  display: flex;
  flex-flow: column nowrap;

  & p {
    font-size: 1rem;
    margin: 0;

    &:first-child {
      font-weight: 500;
      font-size: 0.875rem;
      line-height: 1.5;
      margin: 0;
      color: ${(props) => props.theme.primary500};
    }

    &:nth-child(2) {
      font-weight: 700;
      line-height: 1.5;
      font-size: 1rem;
      color: ${(props) => props.theme.black1000};
    }

    strong {
      font-weight: 600;
    }
  }

  h5 {
    font-size: 0.75rem;
    line-height: 1.5;
    font-weight: 600;
    text-transform: uppercase;
    margin: 0;
    color: ${(props) => props.theme.primary500};
  }

  ul {
    list-style-type: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-flow: column nowrap;
    gap: 1rem;

    li {
      strong {
        font-weight: 600;
        font-size: 0.875rem;
        color: ${(props) => props.theme.black700};
      }
    }
  }
`;

const EventSpeakerRequest = (props) => {
  const { datetime, isAnswerable, available, accepted } = props;

  let date = simpleDateTime(datetime);
  date = `${date[0].toUpperCase()}${date.slice(1)}`;

  return isAnswerable ? (
    <li>
      <strong>
        {date[0].toUpperCase()}
        {date.slice(1)}
      </strong>
      <EventSpeakerRequestForm {...props} />
    </li>
  ) : (
    <li
      css={`
        & + & {
          margin-top: -1rem;
        }
      `}
    >
      <CheckboxField small readOnly value={available} label={date} />
    </li>
  );
};
EventSpeakerRequest.propTypes = {
  datetime: PropTypes.string.isRequired,
  isAnswerable: PropTypes.bool.isRequired,
  available: PropTypes.bool,
};

const EventRequestCard = (props) => {
  const { theme, location, eventSpeakerRequests } = props;
  return (
    <StyledCard>
      <p>
        {theme.type} sur le thème &laquo;&nbsp;{theme.name}&nbsp;&raquo;
      </p>
      <p>
        {location.zip}, {location.city} · {location.country}
      </p>
      <Spacer size="0.5rem" />
      <ul>
        {eventSpeakerRequests.map((eventSpeakerRequest) => (
          <EventSpeakerRequest
            key={eventSpeakerRequest.id}
            {...eventSpeakerRequest}
          />
        ))}
      </ul>
    </StyledCard>
  );
};
EventRequestCard.propTypes = {
  theme: PropTypes.shape({
    name: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    city: PropTypes.string.isRequired,
    zip: PropTypes.string.isRequired,
    country: PropTypes.string.isRequired,
  }).isRequired,
  eventSpeakerRequests: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    }),
  ),
};

export default EventRequestCard;
