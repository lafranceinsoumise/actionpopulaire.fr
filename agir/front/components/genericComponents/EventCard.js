import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo, useRef } from "react";
import styled from "styled-components";

import { displayIntervalEnd, displayIntervalStart } from "@agir/lib/utils/time";

import Map from "@agir/carte/common/Map";
import Link from "@agir/front/app/Link";
import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";
import eventCardDefaultBackground from "@agir/front/genericComponents/images/event-card-default-bg.svg";
import EventGroupsAttendees from "./EventGroupsAttendees";

const StyledLink = styled(Link)``;
const StyledInfo = styled.div``;
const Illustration = styled(Link)`
  background-color: ${({ $img }) => ($img ? "#e5e5e5" : "#fafafa")};
  display: grid;
  isolation: isolate;
  z-index: 0;
  width: 100%;
  max-width: 225px;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-width: 100%;
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

const StyledContainer = styled.div`
  @media (min-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    flex-direction: row;
  }
`;

const StyledCard = styled(Card)`
  border-radius: ${(props) => props.theme.borderRadius};
  width: 100%;
  overflow: hidden;
  padding: 0;
  display: flex;
  flex-direction: column;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    padding: 0;
    box-shadow: none;
    border: 1px solid ${(props) => props.theme.black100};
    min-height: 125px;
  }

  ${Illustration} {
    flex: 0 0 225px;
    margin: 0;
    padding: 0;
    min-height: 125px;
  }

  main {
    margin: 0;
    padding: 1.25rem;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      flex: 1 1 auto;
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

    ${StyledLink} {
      display: inline-block;
      width: auto;
      color: inherit;
      font-weight: 600;
      font-size: 1rem;
      margin: 0.5rem 0;
      line-height: 1.5;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        font-weight: 700;
        margin-top: 0;
      }

      &:hover {
        text-decoration: none;
      }

      &:focus {
        outline: none;
      }
    }

    ${StyledInfo} {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;

      p {
        font-weight: 400;
        font-size: 0.875rem;
        color: ${(props) => props.theme.black700};
        margin: 0 1.5rem 0;
        text-indent: -1.8rem;

        span:first-child {
          vertical-align: sub;
        }

        span + span::before {
          content: ", ";
        }

        span:first-child + span::before {
          content: " ";
        }
      }
    }
  }
`;

const EventCardIllustration = (props) => {
  const { image, coordinates, subtype, staticMapUrl, eventPageLink, eventPk } =
    props;

  const isVisible = useResponsiveMemo(
    !!image || Array.isArray(coordinates),
    true
  );

  const linkProps = useMemo(
    () => ({
      href: eventPageLink || undefined,
      route: !eventPageLink ? "eventDetails" : undefined,
      routeParams: !eventPageLink ? { eventPk } : undefined,
    }),
    [eventPageLink, eventPk]
  );

  if (!isVisible) {
    return null;
  }

  if (image) {
    return (
      <Illustration {...linkProps} $img={image}>
        <img src={image} alt="Image d'illustration" />
      </Illustration>
    );
  }
  if (Array.isArray(coordinates)) {
    return (
      <Illustration {...linkProps}>
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
    <Illustration {...linkProps}>
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
  eventPageLink: PropTypes.string,
  eventPk: PropTypes.string,
};

const EventCard = (props) => {
  const {
    id,
    illustration,
    schedule,
    location,
    distance,
    subtype,
    name,
    groups,
    eventPageLink,
    backLink,
    eventSpeakers,
  } = props;

  const now = DateTime.local();
  const pending = now >= schedule.start && now <= schedule.end;
  const isPast = schedule.isBefore(DateTime.local());
  const linkRef = useRef();
  const eventDate = pending
    ? displayIntervalEnd(schedule)
    : displayIntervalStart(schedule);

  const handleClick = React.useCallback(() => {
    linkRef.current && linkRef.current.click();
  }, []);

  const groupsAttendees = useMemo(() => {
    if (!Array.isArray(props.groupsAttendees)) {
      return [];
    }
    return props.groupsAttendees.filter(
      (group) => !groups.some((g) => g.id === group.id)
    );
  }, [groups, props.groupsAttendees]);

  return (
    <StyledCard onClick={handleClick} $isPast={isPast}>
      <EventGroupsAttendees groupsAttendees={groupsAttendees} isPast={isPast} />
      <StyledContainer>
        <EventCardIllustration
          image={illustration?.thumbnail}
          subtype={subtype}
          coordinates={location?.coordinates?.coordinates}
          staticMapUrl={location?.staticMapUrl}
          eventPageLink={eventPageLink}
          eventPk={id}
        />
        <main>
          <h4>
            {`${eventDate}
              ${
                location && location.shortLocation
                  ? " • " + location.shortLocation
                  : ""
              }${
              location && distance && !isNaN(distance)
                ? ` ⟷ ${Math.round(distance) / 1000} Km`.replace(".", ",")
                : ""
            }`.trim()}
          </h4>
          <StyledLink
            ref={linkRef}
            href={eventPageLink || undefined}
            route={!eventPageLink ? "eventDetails" : undefined}
            routeParams={!eventPageLink ? { eventPk: id } : undefined}
            backLink={backLink}
          >
            {name}
          </StyledLink>
          <StyledInfo>
            {Array.isArray(eventSpeakers) && eventSpeakers.length > 0 ? (
              <p title="Intervenant·es">
                <RawFeatherIcon widht="1rem" height="1rem" name="mic" />
                &nbsp;avec{" "}
                {eventSpeakers
                  .map((speaker, i) => {
                    if (i === 0) {
                      return speaker.name;
                    }
                    return `${eventSpeakers[i] ? "," : " et"} ${speaker.name}`;
                  })
                  .join("")}
              </p>
            ) : null}
            {Array.isArray(groups) && groups.length > 0 ? (
              <p title="Groupes organisateurs">
                <RawFeatherIcon widht="1rem" height="1rem" name="users" />
                {groups.map((group) => (
                  <span key={group.id}>{group.name}</span>
                ))}
              </p>
            ) : null}
          </StyledInfo>
        </main>
      </StyledContainer>
    </StyledCard>
  );
};

EventCard.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
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
  distance: PropTypes.number,
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
    })
  ),
  groupsAttendees: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
    })
  ),
  subtype: PropTypes.object,
  eventPageLink: PropTypes.string,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  eventSpeakers: PropTypes.array,
};

export default EventCard;
