import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";

import { routeConfig } from "@agir/front/app/routes.config";
import Link from "@agir/front/app/Link";
import ActionCard from "@agir/front/genericComponents/ActionCard";
import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";

import { useHistory } from "react-router-dom";

export const requiredActionTypes = [
  "waiting-payment",
  "group-invitation",
  "new-member",
  "waiting-location-group",
  "group-coorganization-invite",
  "waiting-location-event",
  "group-creation-confirmation",
  "group-membership-limit-reminder",
];

const GroupMembershipLimitReminderRequiredActionCard = (props) => {
  const { supportGroup, meta = {}, routes, onDismiss } = props;
  const { membershipCount, membershipLimitNotificationStep } = meta;

  if (!membershipCount || typeof membershipLimitNotificationStep !== "number") {
    return null;
  }

  switch (membershipLimitNotificationStep) {
    case 0:
      return (
        <ActionCard
          iconName="alert-circle"
          confirmLabel="Diviser mon équipe"
          dismissLabel="C'est fait !"
          onConfirm={
            supportGroup.routes && supportGroup.routes.membershipTransfer
          }
          onDismiss={onDismiss}
          text={
            <>
              <strong>
                Action requise&nbsp;: votre équipe ne respecte plus la{" "}
                <a href={routes.charteEquipes}>charte des équipes de soutien</a>
              </strong>
              <br />
              <a href={supportGroup.url}>{supportGroup.name}</a> a atteint{" "}
              {membershipCount} personnes&nbsp;! Il est maintenant impossible
              que des nouvelles personnes la rejoignent. Divisez votre équipe en
              équipes plus petites maintenant pour renforcer le réseau d’action.
            </>
          }
        />
      );
    case 1:
    case 2:
      return (
        <ActionCard
          iconName="alert-circle"
          confirmLabel="Diviser mon équipe"
          dismissLabel="Cacher"
          onConfirm={
            supportGroup.routes && supportGroup.routes.membershipTransfer
          }
          onDismiss={onDismiss}
          text={
            <>
              <strong>Votre équipe est trop nombreuse</strong>
              <br />
              <a href={supportGroup.url}>{supportGroup.name}</a> compte plus de{" "}
              {membershipCount - 1} personnes&nbsp;! Il est temps de vous
              diviser en plusieurs équipes pour permettre une plus grande
              répartition de l’action.{" "}
              <a href={routes.groupTransferHelp}>
                En savoir plus sur la division des équipes
              </a>
            </>
          }
        />
      );
    case 3:
      return (
        <ActionCard
          iconName="info"
          confirmLabel="Diviser mon équipe"
          dismissLabel="Cacher"
          onConfirm={
            supportGroup.routes && supportGroup.routes.membershipTransfer
          }
          onDismiss={onDismiss}
          text={
            <>
              <strong>
                Gardez un oeil sur le nombre de membres de votre équipe
              </strong>
              <br />
              <a href={supportGroup.url}>{supportGroup.name}</a> a dépassé les{" "}
              {membershipCount - 1} personnes ! Afin que chacun·e puisse
              s'impliquer et pour permettre une plus grande répartition de votre
              action, nous vous invitons à diviser votre équipe.{" "}
              <a href={routes.groupTransferHelp}>
                En savoir plus sur la division des équipes
              </a>
            </>
          }
        />
      );
    default:
      return (
        <ActionCard
          iconName="thumbs-up"
          confirmLabel="En savoir plus"
          dismissLabel="Cacher"
          onConfirm={routes.groupTransferHelp}
          onDismiss={onDismiss}
          text={
            <>
              <strong>
                Bravo, vous êtes maintenant {membershipCount} dans votre
                équipe&nbsp;!
              </strong>
              <br />
              <a href={supportGroup.url}>{supportGroup.name}</a> a atteint le
              nombre idéal de personnes. Désormais, favorisez la création
              d'autres équipes autour de chez vous par d’autres membres, de
              manière à renforcer le réseau d'action.
            </>
          }
        />
      );
  }
};
GroupMembershipLimitReminderRequiredActionCard.propTypes = {
  supportGroup: PropTypes.shape({
    name: PropTypes.string.isRequired,
    url: PropTypes.string,
    routes: PropTypes.shape({
      membershipTransfer: PropTypes.string.isRequired,
    }).isRequired,
  }).isRequired,
  meta: PropTypes.shape({
    membershipLimit: PropTypes.number,
    membershipCount: PropTypes.number,
    membershipLimitNotificationStep: PropTypes.number,
  }),
  routes: PropTypes.shape({
    groupTransferHelp: PropTypes.string.isRequired,
    charteEquipes: PropTypes.string.isRequired,
  }).isRequired,
  onDismiss: PropTypes.func,
};

const RequiredActionCard = (props) => {
  const {
    id,
    type,
    event,
    supportGroup,
    individual,
    meta,
    onDismiss,
    routes,
  } = props;

  const handleDismiss = useCallback(() => {
    onDismiss(id);
  }, [id, onDismiss]);

  const [isEmailCopied, copyEmail] = useCopyToClipboard(
    (individual && individual.email) || "",
    1000
  );

  const history = useHistory();
  const Event = useMemo(
    () =>
      event ? (
        <Link
          to={
            routeConfig.eventDetails &&
            routeConfig.eventDetails.getLink({ eventPk: event.id })
          }
        >
          {event.name}
        </Link>
      ) : null,
    [event]
  );

  const goToEventDetails = useCallback(() => {
    event &&
      event.id &&
      routeConfig.eventDetails &&
      history.push(routeConfig.eventDetails.getLink({ eventPk: event.id }));
  }, [event, history]);

  switch (type) {
    case "waiting-payment": {
      return (
        <ActionCard
          iconName="alert-circle"
          confirmLabel="Payer"
          dismissLabel="Voir l'événement"
          onConfirm={event.routes.rsvp}
          onDismiss={goToEventDetails}
          text={
            <>
              Vous n'avez pas encore réglé votre place pour l'événément :{" "}
              {Event}
            </>
          }
        />
      );
    }
    case "group-invitation": {
      return (
        <ActionCard
          iconName="mail"
          confirmLabel="Rejoindre"
          dismissLabel="Décliner"
          onConfirm={(meta && meta.joinUrl) || supportGroup.url}
          onDismiss={handleDismiss}
          text={
            <>
              Vous avez été invité-e à rejoindre le groupe :{" "}
              <a href={supportGroup.url}>{supportGroup.name}</a>
            </>
          }
        />
      );
    }
    case "new-member": {
      return (
        <ActionCard
          iconName="user-plus"
          confirmLabel={isEmailCopied ? "✓ Copié !" : "Copier le mail"}
          dismissLabel="C'est fait"
          onConfirm={copyEmail}
          onDismiss={handleDismiss}
          disabled={isEmailCopied}
          text={
            <>
              <strong>{individual.firstName || "Quelqu'un"}</strong> a rejoint
              votre groupe <a href={supportGroup.url}>{supportGroup.name}</a>.
              Prenez le temps de l’accueillir !
            </>
          }
        />
      );
    }
    case "waiting-location-group": {
      return (
        <ActionCard
          iconName="alert-circle"
          confirmLabel="Mettre à jour"
          onConfirm={supportGroup.url}
          onDismiss={handleDismiss}
          text={
            <>
              Précisez la localisation de votre groupe{" "}
              <a href={supportGroup.url}>{supportGroup.name}</a>
            </>
          }
        />
      );
    }
    case "group-coorganization-invite": {
      return (
        <ActionCard
          iconName="mail"
          confirmLabel="Voir"
          dismissLabel="Décliner"
          onConfirm={goToEventDetails}
          onDismiss={handleDismiss}
          text={
            <>
              <strong>{props.individual.firstName || "Quelqu'un"}</strong> a
              proposé à votre groupe{" "}
              <a href={supportGroup.url}>{supportGroup.name}</a> de co-organiser
              : {Event}
            </>
          }
        />
      );
    }
    case "waiting-location-event": {
      return (
        <ActionCard
          iconName="alert-circle"
          confirmLabel="Mettre à jour"
          onConfirm={event.routes.manage}
          onDismiss={handleDismiss}
          text={<>Précisez la localisation de votre événement :{Event}</>}
        />
      );
    }
    case "group-creation-confirmation": {
      return (
        <ActionCard
          iconName="users"
          confirmLabel="Lire l'article"
          dismissLabel="C'est fait"
          onConfirm={routes && routes.newGroupHelp}
          onDismiss={handleDismiss}
          text={
            <>
              <a href={supportGroup.url}>{supportGroup.name}</a> est en ligne !
              <br />
              <br />
              En tant qu'animateur·ice, vous pouvez gérer{" "}
              <a href={supportGroup.url}>{supportGroup.name}</a> à tout moment
              depuis le bouton &laquo;&nbsp;Gestion&nbsp;&raquo; ou bien en
              cliquant sur{" "}
              <a href={supportGroup.routes && supportGroup.routes.manage}>
                ce lien
              </a>
              .
              <br />
              <br />
              Nous vous conseillons de lire ces conseils à destination des
              nouveaux animateur·ice·s.
            </>
          }
        />
      );
    }
    case "group-membership-limit-reminder": {
      return (
        <GroupMembershipLimitReminderRequiredActionCard
          {...props}
          onDismiss={handleDismiss}
        />
      );
    }
    default:
      return null;
  }
};
RequiredActionCard.propTypes = {
  id: PropTypes.number.isRequired,
  type: PropTypes.string.isRequired,
  event: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    routes: PropTypes.shape({
      addPhoto: PropTypes.string,
      calendarExport: PropTypes.string,
      cancel: PropTypes.string,
      compteRendu: PropTypes.string,
      details: PropTypes.string,
      googleExport: PropTypes.string,
      rsvp: PropTypes.string,
      manage: PropTypes.string,
      map: PropTypes.string,
    }).isRequired,
  }),
  supportGroup: PropTypes.shape({
    name: PropTypes.string,
    url: PropTypes.string,
    routes: PropTypes.shape({
      manage: PropTypes.string,
      membershipTransfer: PropTypes.string,
    }).isRequired,
  }),
  individual: PropTypes.shape({
    firstName: PropTypes.string,
    email: PropTypes.string,
  }),
  onDismiss: PropTypes.func,
  meta: PropTypes.object,
  routes: PropTypes.object,
};
export default RequiredActionCard;
