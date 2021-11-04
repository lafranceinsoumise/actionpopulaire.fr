import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";

import { displayIntervalStart, displayIntervalEnd } from "@agir/lib/utils/time";

import Card from "@agir/front/genericComponents/Card";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Map from "@agir/carte/common/Map";
import Spacer from "@agir/front/genericComponents/Spacer";

import eventCardDefaultBackground from "@agir/front/genericComponents/images/event-card-default-bg.svg";

const Illustration = styled.div`
  background-color: ${({ $img }) => ($img ? "#e5e5e5" : "#fafafa")};
  display: grid;
  isolation: isolate;
  z-index: 0;
  width: 100%;
  max-width: 225px;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: -1rem -1rem 1rem;
    width: calc(100% + 2rem);
    max-width: 100vw;
  }

  & > * {
    grid-column: 1/2;
    grid-row: 1/2;
    z-index: 1;
    max-height: inherit;
    max-width: 100%;
  }

  &::before {
    content: "";
    z-index: 0;
    grid-column: 1/2;
    grid-row: 1/2;
    display: ${({ $img }) => ($img ? "block" : "none")};
    height: 100%;
    width: 100%;
    background-image: url(${({ $img }) => $img});
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center center;
    opacity: 0.25;
  }

  img {
    height: 125px;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      height: 150px;
    }
    margin: 0 auto;
    align-self: center;
  }

  & > * {
    @media (max-width: ${(props) => props.theme.collapse}px) {
      height: 150px;
    }
  }
`;

const StyledCard = styled(Card)`
  border-radius: ${(props) => props.theme.borderRadius};
  width: 100%;
  overflow: hidden;
  padding: 0;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    display: grid;
    grid-template-columns: 225px 1fr;
    grid-template-rows: auto auto;
    padding: 0;
    box-shadow: none;
    border: 1px solid ${(props) => props.theme.black100};
    min-height: 125px;
  }

  ${Illustration} {
    margin: 0;
    padding: 0;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      grid-row: span 2;
    }
  }

  main {
    margin: 0;
    padding: 1.25rem;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      padding: 1.5rem;
      align-self: stretch;
    }

    h4 {
      font-weight: 500;
      font-size: 0.875rem;
      line-height: 1.5;
      margin: 0;
      color: ${(props) =>
        props.$isPast ? props.theme.black500 : props.theme.primary500};
    }

    h3 {
      font-weight: 600;
      font-size: 1rem;
      margin: 0.5rem 0;
      line-height: 1.5;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        font-weight: 700;
        margin-top: 0;
      }
    }

    p {
      font-weight: 400;
      font-size: 0.875rem;
      line-height: 1.5;
      color: ${(props) => props.theme.black700};
      display: flex;
      align-items: center;
      margin: 0;
    }
  }
`;

const EventCardIllustration = (props) => {
  const { image, coordinates, subtype, staticMapUrl } = props;

  const isVisible = useResponsiveMemo(
    !!image || Array.isArray(coordinates),
    true
  );

  if (!isVisible) {
    return null;
  }

  if (image) {
    return (
      <Illustration $img={image}>
        <img src={image} alt="Image d'illustration" />
      </Illustration>
    );
  }
  if (Array.isArray(coordinates)) {
    return (
      <Illustration>
        <Map
          zoom={11}
          center={coordinates}
          iconConfiguration={subtype}
          isStatic
          staticMapUrl={staticMapUrl}
        />
      </Illustration>
    );
  }
  return (
    <Illustration>
      <img
        src={eventCardDefaultBackground}
        width="359"
        height="203"
        alt="Image d'illustration par défaut"
      />
    </Illustration>
  );
};
EventCardIllustration.propTypes = {
  image: PropTypes.string,
  coordinates: PropTypes.array,
  subtype: PropTypes.object,
  staticMapUrl: PropTypes.string,
};

const EventCard = (props) => {
  const {
    id,
    illustration,
    hasSubscriptionForm,
    schedule,
    location,
    subtype,
    name,
    participantCount,
    rsvp,
    routes,
    groups,
    compteRendu,
  } = props;
  const navigate = useNavigate();

  const now = DateTime.local();
  const pending = now >= schedule.start && now <= schedule.end;
  const isPast = schedule.isBefore(DateTime.local());

  const eventDate = pending
    ? displayIntervalEnd(schedule)
    : displayIntervalStart(schedule);

  const handleClick = React.useCallback(
    (e) => {
      if (["A", "BUTTON"].includes(e.target.tagName.toUpperCase())) {
        return;
      }
      id &&
        routeConfig.eventDetails &&
        navigate(routeConfig.eventDetails.getLink({ eventPk: id }));
    },
    [navigate, id]
  );

  return (
    <StyledCard onClick={handleClick} $isPast={isPast}>
      <EventCardIllustration
        image={illustration?.thumbnail}
        subtype={subtype}
        coordinates={location?.coordinates?.coordinates}
        staticMapUrl={location?.staticMapUrl}
      />
      <main>
        <h4>
          {`${eventDate}
            ${
              location && location.shortLocation
                ? " • " + location.shortLocation
                : ""
            }`.trim()}
        </h4>
        <h3>{name}</h3>
        {Array.isArray(groups) && groups.length > 0 ? (
          <p>
            <RawFeatherIcon widht="1rem" height="1rem" name="users" />
            &nbsp;
            {groups.map((group) => group.name).join(", ")}
          </p>
        ) : null}
      </main>
    </StyledCard>
  );
};

EventCard.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  participantCount: PropTypes.number,
  hasSubscriptionForm: PropTypes.bool,
  illustration: PropTypes.shape({
    thumbnail: PropTypes.string,
  }),
  schedule: PropTypes.instanceOf(Interval).isRequired,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    shortLocation: PropTypes.string,
    coordinates: PropTypes.shape({
      coordinates: PropTypes.arrayOf(PropTypes.number),
    }),
    staticMapUrl: PropTypes.string,
  }),
  rsvp: PropTypes.string,
  routes: PropTypes.shape({
    details: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
    compteRendu: PropTypes.string,
  }),
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
    })
  ),
  compteRendu: PropTypes.string,
  subtype: PropTypes.object,
};

export default EventCard;
