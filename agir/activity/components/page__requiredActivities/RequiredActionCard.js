import PropTypes from "prop-types";
import React, { useCallback } from "react";

import ActionCard from "@agir/front/genericComponents/ActionCard";
import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";

export const requiredActionTypes = [
  "waiting-payment",
  "group-invitation",
  "new-member",
  "waiting-location-group",
  "group-coorganization-invite",
  "waiting-location-event",
  "group-creation-confirmation",
];

const RequiredActionCard = (props) => {
  const {
    id,
    type,
    event,
    supportGroup,
    individual,
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

  switch (type) {
    case "waiting-payment": {
      return (
        <ActionCard
          iconName="alert-circle"
          confirmLabel="Payer"
          dismissLabel="Voir l'événement"
          onConfirm={event.routes.rsvp}
          onDismiss={event.routes.details}
          text={
            <>
              Vous n'avez pas encore réglé votre place pour l'événément :{" "}
              <a href={event.routes.details}>{event.name}</a>
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
          onConfirm={supportGroup.url}
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
          onConfirm={event.routes.details}
          onDismiss={handleDismiss}
          text={
            <>
              <strong>{props.individual.firstName || "Quelqu'un"}</strong> a
              proposé à votre groupe{" "}
              <a href={supportGroup.url}>{supportGroup.name}</a> de co-organiser
              : <a href={event.routes.details}>{event.name}</a>
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
          text={
            <>
              Précisez la localisation de votre événement :{" "}
              <a href={event.routes.details}>{event.name}</a>
            </>
          }
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
    default:
      return null;
  }
};
RequiredActionCard.propTypes = {
  id: PropTypes.number.isRequired,
  type: PropTypes.string.isRequired,
  event: PropTypes.shape({
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
    }).isRequired,
  }),
  individual: PropTypes.shape({
    firstName: PropTypes.string,
    email: PropTypes.string,
  }),
  onDismiss: PropTypes.func,
  routes: PropTypes.object,
};
export default RequiredActionCard;
