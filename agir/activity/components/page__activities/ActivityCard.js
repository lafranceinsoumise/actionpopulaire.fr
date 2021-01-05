import Card from "@agir/front/genericComponents/Card";
import React, { useMemo } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { Interval } from "luxon";

import { routeConfig } from "@agir/front/app/routes.config";
import Link from "@agir/front/app/Link";

import EventCard from "@agir/front/genericComponents/EventCard";
import { Column, Row } from "@agir/front/genericComponents/grid";
import style from "@agir/front/genericComponents/_variables.scss";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import { dateFromISOString, displayHumanDate } from "@agir/lib/utils/time";
import { activityStatus } from "@agir/activity/common/helpers";

import CONFIG from "./activity.config.json";

const StyledParagraph = styled.p`
  margin-bottom: 0;
`;

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

const ActivityCardContainer = React.memo((props) => {
  const { status, type, timestamp, event, children } = props;

  const date = useMemo(
    () =>
      displayHumanDate(dateFromISOString(timestamp))
        .split("")
        .map((ch, i) => (i ? ch : ch.toUpperCase()))
        .join(""),
    [timestamp]
  );

  const iconName = useMemo(() => CONFIG[type].icon || "info", [type]);

  const eventSchedule = useMemo(
    () => event && Interval.fromISO(`${event.startTime}/${event.endTime}`),
    [event]
  );

  if (!CONFIG[type]) {
    return null;
  }

  return (
    <LowMarginCard isUnread={status === activityStatus.STATUS_UNDISPLAYED}>
      <Row gutter="8" align="flex-start">
        <Column width="1rem" collapse={0} style={{ paddingTop: "2px" }}>
          <FeatherIcon name={iconName} color={style.black500} />
        </Column>
        <Column collapse={0} grow style={{ fontSize: "15px" }}>
          <StyledParagraph>{children}</StyledParagraph>
          <p
            style={{
              margin: "0.125rem 0 0",
              fontSize: "13px",
              color: style.black700,
              fontWeight: 400,
            }}
          >
            {date}
          </p>
        </Column>
      </Row>
      {CONFIG[type].hasEvent && (
        <EventCardContainer>
          <EventCard {...event} schedule={eventSchedule} />
        </EventCardContainer>
      )}
    </LowMarginCard>
  );
});
ActivityCardContainer.displayName = "ActivityCardContainer";
ActivityCardContainer.propTypes = {
  status: PropTypes.oneOf(Object.values(activityStatus)),
  type: PropTypes.string.isRequired,
  event: PropTypes.object, // see event card PropTypes
  timestamp: PropTypes.string.isRequired,
  children: PropTypes.node,
};

const ReferralUpdateActivityText = (props) => {
  const {
    individual,
    meta: { totalReferrals },
    routes,
  } = props;
  if (totalReferrals < 5) {
    return (
      <ActivityCardContainer {...props}>
        Grâce à vous, {individual || "quelqu'un"} a parrainé la candidature de
        Jean-Luc Mélenchon.
        <br />
        Merci beaucoup, continuez à partager ! 👍
      </ActivityCardContainer>
    );
  }
  if (totalReferrals === 5) {
    return (
      <ActivityCardContainer {...props}>
        5 personnes ont parrainé la candidature de Jean-Luc Mélenchon grâce à
        vous ! La campagne de signature continue, invitez vos amis à partager
        leur lien personnalisé à leur tour !
      </ActivityCardContainer>
    );
  }
  if (totalReferrals < 10) {
    return (
      <ActivityCardContainer {...props}>
        Encore un ! {individual} a parrainé la candidature de Jean-Luc
        Mélenchon.
        <br />
        C'est super, vous avez fait signer {totalReferrals} personnes !
        Continuez comme ça ! 😀
      </ActivityCardContainer>
    );
  }
  if (totalReferrals === 10) {
    return (
      <ActivityCardContainer {...props}>
        Vous avez permis la signature de 10 personnes ! Quel est votre secret ?!
        <br />
        Si vous n'y aviez pas encore songé, il est peut-être temps de{" "}
        <a href={routes.createGroup}>
          créer une équipe de soutien dans votre ville
        </a>{" "}
        ;)
      </ActivityCardContainer>
    );
  }
  if (totalReferrals === 20) {
    return (
      <ActivityCardContainer {...props}>
        Grâce à vous, 20 personnes ont parrainé la candidature de Jean-Luc
        Mélenchon !<br />
        Beau travail ! Prochaine étape :{" "}
        <a href={routes.createEvent}>organiser un événement en ligne</a> pour
        récolter encore plus de signatures !
      </ActivityCardContainer>
    );
  }
  return (
    <ActivityCardContainer {...props}>
      Et de {totalReferrals} ! {individual} a parrainé la candidature de
      Jean-Luc Mélenchon. Génial ! 😍
    </ActivityCardContainer>
  );
};
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

const ActivityCard = (props) => {
  const { type, meta, event, supportGroup, individual } = props;

  const { Event, SupportGroup, Individual } = useMemo(
    () => ({
      Event: event && (
        <Link
          to={
            routeConfig.eventDetails
              ? routeConfig.eventDetails.getLink({ eventPk: event.id })
              : event.routes.details
          }
        >
          {event.name}
        </Link>
      ),
      SupportGroup: supportGroup && (
        <a href={supportGroup.url}>{supportGroup.name}</a>
      ),
      Individual: individual && <strong>{individual.firstName}</strong>,
    }),
    [event, supportGroup, individual]
  );

  if (!CONFIG[type]) {
    return null;
  }

  switch (type) {
    case "waiting-payment":
      return (
        <ActivityCardContainer {...props}>
          Vous n'avez pas encore réglé votre place pour l'événément {Event}
        </ActivityCardContainer>
      );
    case "group-invitation":
      return (
        <ActivityCardContainer {...props}>
          Vous avez été invité⋅e à rejoindre {SupportGroup}
        </ActivityCardContainer>
      );
    case "new-member":
      return (
        <ActivityCardContainer {...props}>
          {Individual || "Quelqu'un"} a rejoint {SupportGroup}. Prenez le temps
          de l’accueillir&nbsp;!
        </ActivityCardContainer>
      );
    case "waiting-location-group":
      return (
        <ActivityCardContainer {...props}>
          Précisez la localisation de {SupportGroup}
        </ActivityCardContainer>
      );
    case "group-coorganization-invite":
      return (
        <ActivityCardContainer {...props}>
          {Individual || "Quelqu'un"} a proposé à {SupportGroup} de co-organiser{" "}
          {Event}
        </ActivityCardContainer>
      );
    case "waiting-location-event":
      return (
        <ActivityCardContainer {...props}>
          Précisez la localisation de votre événement&nbsp;: {Event}
        </ActivityCardContainer>
      );
    case "group-coorganization-accepted":
      return (
        <ActivityCardContainer {...props}>
          {SupportGroup} a accepté de co-organiser votre événement {Event}
        </ActivityCardContainer>
      );
    case "group-info-update":
      return (
        <ActivityCardContainer {...props}>
          {SupportGroup} a été mis à jour
        </ActivityCardContainer>
      );
    case "accepted-invitation-member":
      return (
        <ActivityCardContainer {...props}>
          {Individual || "Quelqu'un"} a rejoint {SupportGroup} en acceptant une
          invitation.
        </ActivityCardContainer>
      );
    case "new-attendee":
      return (
        <ActivityCardContainer {...props}>
          {Individual || "Quelqu'un"} s'est inscrit à votre événement {Event}
        </ActivityCardContainer>
      );
    case "event-update":
      return (
        <ActivityCardContainer {...props}>
          Mise à jour : l'événement {Event} auquel vous participez a changé de
          date.
        </ActivityCardContainer>
      );
    case "new-event-mygroups":
      return (
        <ActivityCardContainer {...props}>
          {SupportGroup || Individual || "Quelqu'un"} a publié un nouvel
          événement
        </ActivityCardContainer>
      );
    case "new-report":
      return (
        <ActivityCardContainer {...props}>
          Le compte-rendu de l'événement {Event} a été ajouté par les
          organisateurs
        </ActivityCardContainer>
      );
    case "new-event-aroundme":
      return (
        <ActivityCardContainer {...props}>
          Un nouvel événement a été publié près de chez vous par{" "}
          {SupportGroup || Individual || "quelqu'un"}
        </ActivityCardContainer>
      );
    case "group-coorganization-info":
      return (
        <ActivityCardContainer {...props}>
          {SupportGroup} a rejoint l'organisation de l'événement {Event}
        </ActivityCardContainer>
      );
    case "cancelled-event":
      return (
        <ActivityCardContainer {...props}>
          L'événement {Event} a été annulé.
        </ActivityCardContainer>
      );
    case "referral-accepted":
      return <ReferralUpdateActivityText {...props} individual={Individual} />;
    case "transferred-group-member":
      return (
        <ActivityCardContainer {...props}>
          Vous avez été transféré·e de &laquo;&nbsp;{meta && meta.oldGroup}
          &nbsp;&raquo; et avez rejoint {SupportGroup}.<br />
          Votre nouvelle équipe vous attend !
        </ActivityCardContainer>
      );
    case "new-members-through-transfer":
      return (
        <ActivityCardContainer {...props}>
          {meta && meta.transferredMemberships} membre
          {meta && meta.transferredMemberships > 0 ? "s" : ""} ont rejoint{" "}
          <a href={supportGroup.routes.manage}>{supportGroup.name}</a> suite à
          un transfert depuis &laquo;&nbsp;
          {meta && meta.oldGroup}&nbsp;&raquo;.
        </ActivityCardContainer>
      );
    default:
      return null;
  }
};
ActivityCard.propTypes = {
  type: PropTypes.string,
  event: PropTypes.object,
  supportGroup: PropTypes.object,
  individual: PropTypes.object,
  routes: PropTypes.object,
  meta: PropTypes.object,
};

export default ActivityCard;
