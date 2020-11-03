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
];

const RequiredActionCard = (props) => {
  const { id, type, event, supportGroup, individual, onDismiss } = props;

  const handleDismiss = useCallback(() => {
    onDismiss(id);
  }, [id]);

  const [isEmailCopied, copyEmail] = useCopyToClipboard(individual.email);

  switch (type) {
    case "waiting-payment": {
      return (
        <ActionCard
          iconName="alert-circle"
          confirmLabel="Payer"
          dismissLabel="Voir l'événement"
          onConfirm={event.routes.details}
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
          text={
            <>
              <strong>{individual.fullName}</strong> a rejoint votre groupe{" "}
              <a href={supportGroup.url}>{supportGroup.name}</a>. Prenez le
              temps de l’accueillir !
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
              <strong>{props.individual.fullName}</strong> a proposé à votre
              groupe <a href={supportGroup.url}>{supportGroup.name}</a> de
              co-organiser : <a href={event.routes.details}>{event.name}</a>
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
          onConfirm={event.routes.details}
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
    default:
      return null;
  }
};
RequiredActionCard.propTypes = {
  id: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  event: PropTypes.shape({
    name: PropTypes.string.isRequired,
    routes: PropTypes.shape({
      details: PropTypes.string.isRequired,
    }).isRequired,
  }),
  supportGroup: PropTypes.shape({
    name: PropTypes.string,
    url: PropTypes.string,
  }),
  individual: PropTypes.shape({
    fullName: PropTypes.string,
    email: PropTypes.string,
  }),
  onDismiss: PropTypes.func,
};
export default RequiredActionCard;
