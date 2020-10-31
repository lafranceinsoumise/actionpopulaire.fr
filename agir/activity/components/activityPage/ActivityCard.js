import Card from "@agir/front/genericComponents/Card";
import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { Interval } from "luxon";

import EventCard from "@agir/front/genericComponents/EventCard";
import { Column, Row } from "@agir/front/genericComponents/grid";
import styles from "@agir/front/genericComponents/style.scss";
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

const ActivityText = ({ type, event, supportGroup, individual }) => {
  return {
    "waiting-payment": (
      <>Vous n'avez pas encore réglé votre place pour l'événément {event}</>
    ),
    "group-invitation": (
      <>Vous avez été invité⋅e à rejoindre le groupe {supportGroup}</>
    ),
    "new-member": (
      <>
        {individual} a rejoint votre groupe {supportGroup}. Prenez le temps de
        l’accueillir&nbsp;!
      </>
    ),
    "waiting-location-group": (
      <>Précisez la localisation de votre groupe {supportGroup}</>
    ),
    "group-coorganization-invite": (
      <>
        {individual} a proposé à votre groupe {supportGroup} de co-organiser{" "}
        {event}
      </>
    ),
    "waiting-location-event": (
      <>Précisez la localisation de votre événement&nbsp;: {event}</>
    ),
    "group-coorganization-accepted": (
      <>
        {supportGroup} a accepté de co-organiser votre événement {event}
      </>
    ),
    "group-info-update": <>Votre groupe {supportGroup} a été mis à jour</>,
    "accepted-invitation-member": (
      <>
        {individual} a rejoint {supportGroup} en acceptant une invitation.
      </>
    ),
    "new-attendee": (
      <>
        {individual} s'est inscrit à votre événement {event}
      </>
    ),
    "event-update": (
      <>
        Mise à jour : l'événement {event} auquel vous participez a changé de
        date.
      </>
    ),
    "new-event-mygroups": (
      <>{supportGroup || individual} a publié un nouvel événement</>
    ),
    "new-report": (
      <>
        Le compte-rendu de l'événement {event} a été ajouté par les
        organisateurs
      </>
    ),
    "new-event-aroundme": (
      <>
        Un nouvel événement a été publié près de chez vous par{" "}
        {supportGroup || individual}
      </>
    ),
    "group-coorganization-info": (
      <>
        Votre groupe {supportGroup} a rejoint l'organisation de l'événement{" "}
        {event}
      </>
    ),
    "cancelled-event": <>L'événement {event} a été annulé.</>,
  }[type];
};

const LowMarginCard = styled(Card)`
  padding: 1rem;
`;

const EventCardContainer = styled.div`
  margin-top: 1rem;

  @media only screen and (min-width: ${styles.collapse}px) {
    padding-left: 2.5rem;
  }

  & ${Card} {
    box-shadow: none;
    border: 1px solid ${styles.black100};
  }
`;

const ActivityCard = (props) => {
  let timestamp = dateFromISOString(props.timestamp);

  let textProps = {
    type: props.type,
    event: props.event && (
      <b>
        <a href={props.event.routes.details}>{props.event.name}</a>
      </b>
    ),
    supportGroup: props.supportGroup && (
      <b>
        <a href={props.supportGroup.url}>{props.supportGroup.name}</a>
      </b>
    ),
    individual: props.individual && <b>{props.individual.fullName}</b>,
  };

  const event = props.event && {
    ...props.event,
    schedule: Interval.fromISO(
      `${props.event.startTime}/${props.event.endTime}`
    ),
  };

  return (
    <LowMarginCard>
      <Row gutter="8" align="center">
        <Column width="1rem" collapse={0} style={{ paddingTop: "2px" }}>
          <FeatherIcon
            name={activityCardIcons[props.type]}
            color={styles.black500}
          />
        </Column>
        <Column collapse={0} grow style={{ fontSize: "15px" }}>
          <ActivityText {...textProps} />
        </Column>
      </Row>
      <div
        style={{
          paddingLeft: "2.5rem",
          fontSize: "15px",
          color: styles.black700,
        }}
      >
        {displayHumanDate(timestamp)}
      </div>

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
