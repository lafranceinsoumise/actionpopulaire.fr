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
import { activityStatus } from "@agir/activity/common/helpers";

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
  "referral-accepted": "share-2",
};

const StyledParagraph = styled.p`
  margin-bottom: 0;
`;

const ReferralUpdateActivityText = React.memo(
  ({ individual, totalReferrals }) => {
    if (totalReferrals < 5) {
      return (
        <StyledParagraph>
          Grâce à vous, {individual || "quelqu'un"} a parrainé la candidature de
          Jean-Luc Mélenchon.
          <br />
          Merci beaucoup, continuez à partager ! 👍
        </StyledParagraph>
      );
    }
    if (totalReferrals < 10) {
      return (
        <StyledParagraph>
          Encore un ! {individual} a parrainé la candidature de Jean-Luc
          Mélenchon.
          <br />
          C'est super, vous avez fait signer {totalReferrals} personnes !
          Continuez comme ça ! 😀
        </StyledParagraph>
      );
    }
    return (
      <StyledParagraph>
        Et de {totalReferrals} ! {individual} a parrainé la candidature de
        Jean-Luc Mélenchon. Génial ! 😍
      </StyledParagraph>
    );
  }
);
ReferralUpdateActivityText.displayName = "ReferralUpdateActivityText";
ReferralUpdateActivityText.propTypes = {
  individual: PropTypes.node,
  totalReferrals: PropTypes.number,
};
const ActivityText = React.memo((props) => {
  const { type, event, supportGroup, individual } = props;
  return {
    "waiting-payment": (
      <StyledParagraph>
        Vous n'avez pas encore réglé votre place pour l'événément {event}
      </StyledParagraph>
    ),
    "group-invitation": (
      <StyledParagraph>
        Vous avez été invité⋅e à rejoindre {supportGroup}
      </StyledParagraph>
    ),
    "new-member": (
      <StyledParagraph>
        {individual || "Quelqu'un"} a rejoint {supportGroup}. Prenez le temps de
        l’accueillir&nbsp;!
      </StyledParagraph>
    ),
    "waiting-location-group": (
      <StyledParagraph>
        Précisez la localisation de {supportGroup}
      </StyledParagraph>
    ),
    "group-coorganization-invite": (
      <StyledParagraph>
        {individual || "Quelqu'un"} a proposé à {supportGroup} de co-organiser{" "}
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
      <StyledParagraph>{supportGroup} a été mis à jour</StyledParagraph>
    ),
    "accepted-invitation-member": (
      <StyledParagraph>
        {individual || "Quelqu'un"} a rejoint {supportGroup} en acceptant une
        invitation.
      </StyledParagraph>
    ),
    "new-attendee": (
      <StyledParagraph>
        {individual || "Quelqu'un"} s'est inscrit à votre événement {event}
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
        {supportGroup || individual || "Quelqu'un"} a publié un nouvel événement
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
        {supportGroup || individual || "quelqu'un"}
      </StyledParagraph>
    ),
    "group-coorganization-info": (
      <StyledParagraph>
        {supportGroup} a rejoint l'organisation de l'événement {event}
      </StyledParagraph>
    ),
    "cancelled-event": (
      <StyledParagraph>L'événement {event} a été annulé.</StyledParagraph>
    ),
    "referral-accepted": <ReferralUpdateActivityText {...props} />,
  }[type];
});
ActivityText.displayName = "ActivityText";
ActivityText.propTypes = {
  type: PropTypes.string,
  event: PropTypes.node,
  supportGroup: PropTypes.node,
  individual: PropTypes.node,
  totalReferrals: PropTypes.number,
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
  const { supportGroup, type, individual, status, meta } = props;
  let { timestamp, event } = props;

  timestamp = dateFromISOString(timestamp);

  let textProps = {
    type: type,
    event: event && <a href={event.routes.details}>{event.name}</a>,
    supportGroup: supportGroup && (
      <a href={supportGroup.url}>{supportGroup.name}</a>
    ),
    individual: individual && <strong>{individual.firstName}</strong>,
    totalReferrals: meta && meta.totalReferrals,
  };

  event = event && {
    ...event,
    schedule: Interval.fromISO(`${event.startTime}/${event.endTime}`),
  };

  if (!activityCardIcons[props.type]) {
    return null;
  }

  return (
    <LowMarginCard isUnread={status === activityStatus.STATUS_UNDISPLAYED}>
      <Row gutter="8" align="flex-start">
        <Column width="1rem" collapse={0} style={{ paddingTop: "2px" }}>
          <FeatherIcon name={activityCardIcons[type]} color={style.black500} />
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
      {eventCardTypes.includes(type) && (
        <EventCardContainer>
          <EventCard {...event} />
        </EventCardContainer>
      )}
    </LowMarginCard>
  );
};

ActivityCard.propTypes = {
  id: PropTypes.number.isRequired,
  type: PropTypes.string.isRequired,
  status: PropTypes.oneOf(Object.values(activityStatus)),
  event: PropTypes.object, // see event card PropTypes
  supportGroup: PropTypes.shape({
    name: PropTypes.string,
    url: PropTypes.string,
  }),
  individual: PropTypes.shape({ firstName: PropTypes.string }),
  meta: PropTypes.shape({
    totalReferrals: PropTypes.number,
  }),
  timestamp: PropTypes.string.isRequired,
};

export default ActivityCard;
