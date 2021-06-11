import PropTypes from "prop-types";
import React, { useMemo } from "react";

import { CHANGED_DATA_LABEL } from "@agir/activity/common/helpers";
import { dateFromISOString } from "@agir/lib/utils/time";

import { getGenderedWord } from "@agir/lib/utils/display";
import { routeConfig } from "@agir/front/app/routes.config";

import Link from "@agir/front/app/Link";
import GenericCardContainer from "./GenericCardContainer";

const GenericCard = (props) => {
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
      Individual: individual && <strong>{individual.displayName}</strong>,
    }),
    [event, supportGroup, individual]
  );

  const changedDataLabel = useMemo(() => {
    let changedDataLabel = "";
    if (meta && Array.isArray(meta.changed_data)) {
      const labels = [];
      meta.changed_data.forEach((field) => {
        if (
          !!CHANGED_DATA_LABEL[field] &&
          !labels.includes(CHANGED_DATA_LABEL[field])
        ) {
          labels.push(CHANGED_DATA_LABEL[field]);
        }
      });
      changedDataLabel = labels
        .map((label, i) => {
          if (i === 0) {
            return ` de ${label}`;
          }
          if (i === labels.length - 1) {
            return ` et de ${label}`;
          }
          return `, de ${label}`;
        })
        .join("");
    }
    return changedDataLabel;
  }, [meta]);

  switch (type) {
    case "waiting-payment": {
      return (
        <GenericCardContainer {...props}>
          Vous n'avez pas encore réglé votre place pour l'événément {Event}
        </GenericCardContainer>
      );
    }
    case "group-invitation": {
      return (
        <GenericCardContainer {...props}>
          Vous avez été invité⋅e à rejoindre {SupportGroup}
        </GenericCardContainer>
      );
    }
    case "new-member": {
      return (
        <GenericCardContainer {...props}>
          {Individual || "Quelqu'un"} a rejoint {SupportGroup}. Prenez le temps
          de l’accueillir&nbsp;!
        </GenericCardContainer>
      );
    }
    case "waiting-location-group": {
      return (
        <GenericCardContainer {...props}>
          Précisez la localisation de {SupportGroup}
        </GenericCardContainer>
      );
    }
    case "group-coorganization-invite": {
      return (
        <GenericCardContainer {...props}>
          {Individual || "Quelqu'un"} a proposé à {SupportGroup} de co-organiser{" "}
          {Event}
        </GenericCardContainer>
      );
    }
    case "waiting-location-event": {
      return (
        <GenericCardContainer {...props}>
          Précisez la localisation de votre événement&nbsp;: {Event}
        </GenericCardContainer>
      );
    }
    case "group-coorganization-accepted":
      return (
        <GenericCardContainer {...props}>
          {SupportGroup} a accepté de co-organiser votre événement {Event}
        </GenericCardContainer>
      );
    case "group-info-update":
      return (
        <GenericCardContainer {...props}>
          {SupportGroup} a été mis à jour
        </GenericCardContainer>
      );
    case "accepted-invitation-member":
      return (
        <GenericCardContainer {...props}>
          {Individual || "Quelqu'un"} a rejoint {SupportGroup} en acceptant une
          invitation.
        </GenericCardContainer>
      );
    case "new-attendee":
      return (
        <GenericCardContainer {...props}>
          <strong>
            {(individual && individual.displayName) || "Quelqu'un"}
          </strong>{" "}
          s'est {getGenderedWord(individual && individual.gender, "inscrit·e")}{" "}
          à votre événement {Event}
        </GenericCardContainer>
      );
    case "event-update": {
      return (
        <GenericCardContainer {...props}>
          Mise à jour : l'événement {Event} auquel vous participez a changé
          {changedDataLabel}.
        </GenericCardContainer>
      );
    }
    case "new-event-mygroups":
      return (
        <GenericCardContainer {...props}>
          {SupportGroup || Individual || "Quelqu'un"} a publié un nouvel
          événement
        </GenericCardContainer>
      );
    case "new-report":
      return (
        <GenericCardContainer {...props}>
          Le compte-rendu de l'événement {Event} a été ajouté par les
          organisateurs
        </GenericCardContainer>
      );
    case "event-suggestion":
      return (
        <GenericCardContainer {...props}>
          Ce{" "}
          {dateFromISOString(event.startTime).toLocaleString({
            weekday: "long",
          })}
          {" : "}
          {event.name} de {SupportGroup || Individual}
        </GenericCardContainer>
      );
    case "group-coorganization-info":
      return (
        <GenericCardContainer {...props}>
          {SupportGroup} a rejoint l'organisation de l'événement {Event}
        </GenericCardContainer>
      );
    case "cancelled-event":
      return (
        <GenericCardContainer {...props}>
          L'événement {Event} a été annulé.
        </GenericCardContainer>
      );
    case "transferred-group-member":
      return (
        <GenericCardContainer {...props}>
          Vous avez été transféré·e de &laquo;&nbsp;{meta && meta.oldGroup}
          &nbsp;&raquo; et avez rejoint {SupportGroup}.<br />
          Votre nouvelle équipe vous attend !
        </GenericCardContainer>
      );
    case "new-members-through-transfer":
      return (
        <GenericCardContainer {...props}>
          {meta && meta.transferredMemberships} membre
          {meta && meta.transferredMemberships > 0 ? "s" : ""} ont rejoint{" "}
          <a href={supportGroup.routes.manage}>{supportGroup.name}</a> suite à
          un transfert depuis &laquo;&nbsp;
          {meta && meta.oldGroup}&nbsp;&raquo;.
        </GenericCardContainer>
      );
    case "group-creation-confirmation": {
      return (
        <GenericCardContainer {...props}>
          {SupportGroup} est en ligne !<br />
          En tant qu'animateur·ice, vous pouvez gérer {SupportGroup} à tout
          moment depuis le bouton &laquo;&nbsp;Gestion&nbsp;&raquo; ou bien en
          cliquant sur{" "}
          <Link
            to={routeConfig.groupSettings.getLink({ groupPk: supportGroup.id })}
          >
            ce lien
          </Link>
          .<br />
          Nous vous conseillons de lire ces conseils à destination des nouveaux
          animateur·ice·s.
        </GenericCardContainer>
      );
    }
    default:
      return null;
  }
};
GenericCard.propTypes = {
  type: PropTypes.string,
  event: PropTypes.object,
  supportGroup: PropTypes.object,
  individual: PropTypes.object,
  routes: PropTypes.object,
  meta: PropTypes.object,
  announcement: PropTypes.object,
};

export default GenericCard;
