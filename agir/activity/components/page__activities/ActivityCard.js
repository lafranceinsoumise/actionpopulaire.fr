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
  "transferred-group-member": "info",
  "new-members-through-transfer": "user-plus",
};

const StyledParagraph = styled.p`
  margin-bottom: 0;
`;

const ReferralUpdateActivityText = React.memo(
  ({ individual, meta: { totalReferrals }, routes }) => {
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
    if (totalReferrals === 5) {
      return (
        <StyledParagraph>
          5 personnes ont parrainé la candidature de Jean-Luc Mélenchon grâce à
          vous ! La campagne de signature continue, invitez vos amis à partager
          leur lien personnalisé à leur tour !
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
    if (totalReferrals === 10) {
      return (
        <StyledParagraph>
          Vous avez permis la signature de 10 personnes ! Quel est votre secret
          ?!
          <br />
          Si vous n'y aviez pas encore songé, il est peut-être temps de{" "}
          <a href={routes.createGroup}>
            créer une équipe de soutien dans votre ville
          </a>{" "}
          ;)
        </StyledParagraph>
      );
    }
    if (totalReferrals === 20) {
      return (
        <StyledParagraph>
          Grâce à vous, 20 personnes ont parrainé la candidature de Jean-Luc
          Mélenchon !<br />
          Beau travail ! Prochaine étape :{" "}
          <a href={routes.createEvent}>organiser un événement en ligne</a> pour
          récolter encore plus de signatures !
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
  meta: PropTypes.shape({
    totalReferrals: PropTypes.number.isRequired,
  }).isRequired,
  routes: PropTypes.shape({
    createEvent: PropTypes.string,
    createGroup: PropTypes.string,
  }),
};
const ActivityText = React.memo((props) => {
  const {
    type,
    event,
    supportGroup,
    supportGroupManage,
    individual,
    meta,
  } = props;
  switch (type) {
    case "waiting-payment":
      return (
        <StyledParagraph>
          Vous n'avez pas encore réglé votre place pour l'événément {event}
        </StyledParagraph>
      );
    case "group-invitation":
      return (
        <StyledParagraph>
          Vous avez été invité⋅e à rejoindre {supportGroup}
        </StyledParagraph>
      );
    case "new-member":
      return (
        <StyledParagraph>
          {individual || "Quelqu'un"} a rejoint {supportGroup}. Prenez le temps
          de l’accueillir&nbsp;!
        </StyledParagraph>
      );
    case "waiting-location-group":
      return (
        <StyledParagraph>
          Précisez la localisation de {supportGroup}
        </StyledParagraph>
      );
    case "group-coorganization-invite":
      return (
        <StyledParagraph>
          {individual || "Quelqu'un"} a proposé à {supportGroup} de co-organiser{" "}
          {event}
        </StyledParagraph>
      );
    case "waiting-location-event":
      return (
        <StyledParagraph>
          Précisez la localisation de votre événement&nbsp;: {event}
        </StyledParagraph>
      );
    case "group-coorganization-accepted":
      return (
        <StyledParagraph>
          {supportGroup} a accepté de co-organiser votre événement {event}
        </StyledParagraph>
      );
    case "group-info-update":
      return <StyledParagraph>{supportGroup} a été mis à jour</StyledParagraph>;
    case "accepted-invitation-member":
      return (
        <StyledParagraph>
          {individual || "Quelqu'un"} a rejoint {supportGroup} en acceptant une
          invitation.
        </StyledParagraph>
      );
    case "new-attendee":
      return (
        <StyledParagraph>
          {individual || "Quelqu'un"} s'est inscrit à votre événement {event}
        </StyledParagraph>
      );
    case "event-update":
      return (
        <StyledParagraph>
          Mise à jour : l'événement {event} auquel vous participez a changé de
          date.
        </StyledParagraph>
      );
    case "new-event-mygroups":
      return (
        <StyledParagraph>
          {supportGroup || individual || "Quelqu'un"} a publié un nouvel
          événement
        </StyledParagraph>
      );
    case "new-report":
      return (
        <StyledParagraph>
          Le compte-rendu de l'événement {event} a été ajouté par les
          organisateurs
        </StyledParagraph>
      );
    case "new-event-aroundme":
      return (
        <StyledParagraph>
          Un nouvel événement a été publié près de chez vous par{" "}
          {supportGroup || individual || "quelqu'un"}
        </StyledParagraph>
      );
    case "group-coorganization-info":
      return (
        <StyledParagraph>
          {supportGroup} a rejoint l'organisation de l'événement {event}
        </StyledParagraph>
      );
    case "cancelled-event":
      return (
        <StyledParagraph>L'événement {event} a été annulé.</StyledParagraph>
      );
    case "referral-accepted":
      return <ReferralUpdateActivityText {...props} />;
    case "transferred-group-member":
      return (
        <StyledParagraph>
          Vous avez été transféré·e de &laquo;&nbsp;{meta && meta.oldGroup}
          &nbsp;&raquo; et avez rejoint {supportGroup}.<br />
          Votre nouvelle équipe vous attend !
        </StyledParagraph>
      );
    case "new-members-through-transfer":
      return (
        <StyledParagraph>
          {meta && meta.transferredMemberships} membre
          {meta && meta.transferredMemberships > 0 ? "s" : ""} ont rejoint{" "}
          {supportGroupManage} suite à un transfert depuis &laquo;&nbsp;
          {meta && meta.oldGroup}&nbsp;&raquo;.
        </StyledParagraph>
      );
    default:
      return null;
  }
});
ActivityText.displayName = "ActivityText";
ActivityText.propTypes = {
  type: PropTypes.string,
  event: PropTypes.node,
  supportGroup: PropTypes.node,
  supportGroupManage: PropTypes.node,
  individual: PropTypes.node,
  routes: PropTypes.object,
  meta: PropTypes.object,
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
  const { routes, supportGroup, type, individual, status, meta } = props;
  let { timestamp, event } = props;

  timestamp = dateFromISOString(timestamp);

  let textProps = {
    type: type,
    event: event && <a href={event.routes.details}>{event.name}</a>,
    supportGroup: supportGroup && (
      <a href={supportGroup.url}>{supportGroup.name}</a>
    ),
    supportGroupManage: supportGroup && supportGroup.routes && (
      <a href={supportGroup.routes.manage}>{supportGroup.name}</a>
    ),
    individual: individual && <strong>{individual.firstName}</strong>,
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
          <ActivityText {...textProps} routes={routes} meta={meta} />
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
    routes: PropTypes.object,
  }),
  individual: PropTypes.shape({ firstName: PropTypes.string }),
  meta: PropTypes.shape({
    totalReferrals: PropTypes.number,
    oldGroup: PropTypes.string,
    transferredMemberships: PropTypes.number,
  }),
  timestamp: PropTypes.string.isRequired,
  routes: PropTypes.object,
};

export default ActivityCard;
