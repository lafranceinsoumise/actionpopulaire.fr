import Card from "@agir/front/genericComponents/Card";
import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { Interval } from "luxon";

import EventCard from "@agir/front/genericComponents/EventCard";
import { Column, Row } from "@agir/front/genericComponents/grid";
import style from "@agir/front/genericComponents/_variables.scss";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import { dateFromISOString, displayHumanDate } from "@agir/lib/utils/time";

const eventCardTypes = [
  "group-coorganization-accepted",
  "event-update",
  "new-event-mygroups",
  "new-report",
  "new-event-aroundme",
  "group-coorganization-info",
];

export const activityCardIcons = {
  "waiting-payment": "alert-circle",
  "group-invitation": "mail",
  "new-member": "user-plus",
  "waiting-location-group": "alert-circle",
  "group-coorganization-invite": "mail",
  "waiting-location-event": "alert-circle",
  "group-coorganization-accepted": "calendar",
  "group-info-update": "info",
  "accepted-invitation-member": "user-plus",
  "new-attendee": "user-plus",
  "event-update": "info",
  "new-event-mygroups": "calendar",
  "new-report": "file-text",
  "new-event-aroundme": "calendar",
  "group-coorganization-info": "calendar",
  "cancelled-event": "x-circle",
};

const StyledParagraph = styled.p`
  margin-bottom: 0;
`;
const ActivityText = ({ type, event, supportGroup, individual }) => {
  return {
    "waiting-payment": (
      <StyledParagraph>
        Vous n'avez pas encore réglé votre place pour l'événément {event}
      </StyledParagraph>
    ),
    "group-invitation": (
      <StyledParagraph>
        Vous avez été invité⋅e à rejoindre le groupe {supportGroup}
      </StyledParagraph>
    ),
    "new-member": (
      <StyledParagraph>
        {individual} a rejoint votre groupe {supportGroup}. Prenez le temps de
        l’accueillir&nbsp;!
      </StyledParagraph>
    ),
    "waiting-location-group": (
      <StyledParagraph>
        Précisez la localisation de votre groupe {supportGroup}
      </StyledParagraph>
    ),
    "group-coorganization-invite": (
      <StyledParagraph>
        {individual} a proposé à votre groupe {supportGroup} de co-organiser{" "}
        {event}
      </StyledParagraph>
    ),
    "waiting-location-event": (
      <StyledParagraph>
        Précisez la localisation de votre événement&nbsp;: {event}
      </StyledParagraph>
    ),
    "group-coorganization-accepted": (
      <StyledParagraph>
        {supportGroup} a accepté de co-organiser votre événement {event}
      </StyledParagraph>
    ),
    "group-info-update": (
      <StyledParagraph>
        Votre groupe {supportGroup} a été mis à jour
      </StyledParagraph>
    ),
    "accepted-invitation-member": (
      <StyledParagraph>
        {individual} a rejoint {supportGroup} en acceptant une invitation.
      </StyledParagraph>
    ),
    "new-attendee": (
      <StyledParagraph>
        {individual} s'est inscrit à votre événement {event}
      </StyledParagraph>
    ),
    "event-update": (
      <StyledParagraph>
        Mise à jour : l'événement {event} auquel vous participez a changé de
        date.
      </StyledParagraph>
    ),
    "new-event-mygroups": (
      <StyledParagraph>
        {supportGroup || individual} a publié un nouvel événement
      </StyledParagraph>
    ),
    "new-report": (
      <StyledParagraph>
        Le compte-rendu de l'événement {event} a été ajouté par les
        organisateurs
      </StyledParagraph>
    ),
    "new-event-aroundme": (
      <StyledParagraph>
        Un nouvel événement a été publié près de chez vous par{" "}
        {supportGroup || individual}
      </StyledParagraph>
    ),
    "group-coorganization-info": (
      <StyledParagraph>
        Votre groupe {supportGroup} a rejoint l'organisation de l'événement{" "}
        {event}
      </StyledParagraph>
    ),
    "cancelled-event": (
      <StyledParagraph>L'événement {event} a été annulé.</StyledParagraph>
    ),
  }[type];
};

const LowMarginCard = styled(Card)`
  @media only screen and (min-width: ${style.collapse}px) {
    padding: 0;
    border: none;
  }
  p {
    & > strong,
    & > a {
      font-weight: 600;
      text-decoration: none;
    }
  }
`;

const EventCardContainer = styled.div`
  margin-top: 1rem;

  @media only screen and (min-width: ${style.collapse}px) {
    padding-left: 2.5rem;
    margin-bottom: 1.5rem;
  }

  & ${Card} {
    box-shadow: none;
    border: 1px solid ${style.black100};
  }
`;

const ActivityCard = (props) => {
  let timestamp = dateFromISOString(props.timestamp);

  let textProps = {
    type: props.type,
    event: props.event && (
      <a href={props.event.routes.details}>{props.event.name}</a>
    ),
    supportGroup: props.supportGroup && (
      <a href={props.supportGroup.url}>{props.supportGroup.name}</a>
    ),
    individual: props.individual && (
      <strong>{props.individual.fullName}</strong>
    ),
  };

  const event = props.event && {
    ...props.event,
    schedule: Interval.fromISO(
      `${props.event.startTime}/${props.event.endTime}`
    ),
  };

  return (
    <LowMarginCard>
      <Row gutter="8" align="flex-start">
        <Column width="1rem" collapse={0} style={{ paddingTop: "2px" }}>
          <FeatherIcon
            name={activityCardIcons[props.type]}
            color={style.black500}
          />
        </Column>
        <Column collapse={0} grow style={{ fontSize: "15px" }}>
          <ActivityText {...textProps} />
          <p
            style={{
              margin: "0.125rem 0 0",
              fontSize: "13px",
              color: style.black700,
              fontWeight: 400,
            }}
          >
            {displayHumanDate(timestamp)
              .split("")
              .map((ch, i) => (i ? ch : ch.toUpperCase()))
              .join("")}
          </p>
        </Column>
      </Row>
      {eventCardTypes.includes(props.type) && (
        <EventCardContainer>
          <EventCard {...event} />
        </EventCardContainer>
      )}
    </LowMarginCard>
  );
};

ActivityCard.propTypes = {
  type: PropTypes.string.isRequired,
  event: PropTypes.object, // see event card PropTypes
  supportGroup: PropTypes.shape({
    name: PropTypes.string,
    url: PropTypes.string,
  }),
  individual: PropTypes.shape({ fullName: PropTypes.string }),
  timestamp: PropTypes.string.isRequired,
};

export default ActivityCard;
