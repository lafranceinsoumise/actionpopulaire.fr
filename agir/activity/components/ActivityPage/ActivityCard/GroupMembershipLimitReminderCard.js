import PropTypes from "prop-types";
import React from "react";

import GenericCardContainer from "./GenericCardContainer";

const GroupMembershipLimitReminderCard = (props) => {
  const { supportGroup, meta = {}, routes } = props;
  const { membershipCount, membershipLimitNotificationStep } = meta;
  switch (membershipLimitNotificationStep) {
    case 0:
      return (
        <GenericCardContainer {...props}>
          <strong>
            Action requise&nbsp;: votre équipe ne respecte plus la{" "}
            <a href={routes.charteEquipes}>charte des équipes de soutien</a>
          </strong>
          <br />
          <a href={supportGroup.url}>{supportGroup.name}</a> a atteint{" "}
          {membershipCount} personnes&nbsp;! Il est maintenant impossible que
          des nouvelles personnes la rejoignent. Divisez votre équipe en équipes
          plus petites maintenant pour renforcer le réseau d’action.
        </GenericCardContainer>
      );
    case 1:
    case 2:
      return (
        <GenericCardContainer {...props}>
          <strong>Votre équipe est trop nombreuse</strong>
          <br />
          <a href={supportGroup.url}>{supportGroup.name}</a> compte plus de{" "}
          {membershipCount - 1} personnes&nbsp;! Il est temps de vous diviser en
          plusieurs équipes pour permettre une plus grande répartition de
          l’action.{" "}
          <a href={routes.groupTransferHelp}>
            En savoir plus sur la division des équipes
          </a>
        </GenericCardContainer>
      );
    case 3:
      return (
        <GenericCardContainer {...props}>
          <strong>
            Gardez un oeil sur le nombre de membres de votre équipe
          </strong>
          <br />
          <a href={supportGroup.url}>{supportGroup.name}</a> a dépassé les{" "}
          {membershipCount - 1} personnes ! Afin que chacun·e puisse s'impliquer
          et pour permettre une plus grande répartition de votre action, nous
          vous invitons à diviser votre équipe.{" "}
          <a href={routes.groupTransferHelp}>
            En savoir plus sur la division des équipes
          </a>
        </GenericCardContainer>
      );
    default:
      return (
        <GenericCardContainer {...props}>
          <strong>
            Bravo, vous êtes maintenant {membershipCount || "nombreux·ses"} dans
            votre équipe&nbsp;!
          </strong>
          <br />
          <a href={supportGroup.url}>{supportGroup.name}</a> a atteint le nombre
          idéal de personnes. Désormais, favorisez la création d'autres équipes
          autour de chez vous par d’autres membres, de manière à renforcer le
          réseau d'action.
        </GenericCardContainer>
      );
  }
};
GroupMembershipLimitReminderCard.propTypes = {
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
  timestamp: PropTypes.string,
  config: PropTypes.shape({
    icon: PropTypes.string,
  }),
};

export default GroupMembershipLimitReminderCard;
