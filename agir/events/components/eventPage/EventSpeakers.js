import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Avatar from "@agir/front/genericComponents/Avatar";
import Card from "@agir/front/genericComponents/Card";

const StyledEventSpeaker = styled.div`
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: 1fr auto;
  grid-auto-flow: dense;
  align-items: center;
  gap: 0 1rem;
  color: ${(props) => props.theme.black500};
  font-weight: 400;
  font-size: 1rem;
  line-height: 1.5;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    font-size: 0.875rem;
  }

  & > * {
    display: block;

    &:empty:not(${Avatar}) {
      display: none;
    }
  }

  ${Avatar} {
    grid-row: span 2;
    width: 2rem;
    height: 2rem;
  }

  strong {
    color: ${(props) => props.theme.black1000};
  }
`;
const StyledCard = styled(Card)`
  display: flex;
  flex-flow: column nowrap;
  gap: 0.5rem;
  padding: 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1.5rem;
  }

  h5 {
    font-size: 1rem;
    line-height: 1.5;
    font-weight: 700;
    color: ${(props) => props.theme.black500};
    margin: 0;
  }
`;

const EventSpeakers = ({ eventSpeakers, ...rest }) => {
  if (!Array.isArray(eventSpeakers) || eventSpeakers.length === 0) {
    return null;
  }

  return (
    <StyledCard {...rest}>
      <h5>Intervenant·e{eventSpeakers.length > 1 && "s"}&nbsp;:</h5>
      {eventSpeakers.map((speaker) => (
        <StyledEventSpeaker key={speaker.id}>
          <Avatar displayName={speaker.name} image={speaker.image} />
          <strong>{speaker.name}</strong>
          <span>{speaker.description}</span>
        </StyledEventSpeaker>
      ))}
    </StyledCard>
  );
};
EventSpeakers.propTypes = {
  eventSpeakers: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
      description: PropTypes.string,
      image: PropTypes.string,
    }),
  ),
};
export default EventSpeakers;
