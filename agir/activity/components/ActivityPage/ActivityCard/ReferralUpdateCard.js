import PropTypes from "prop-types";
import React from "react";

import Link from "@agir/front/app/Link";

import GenericCardContainer from "./GenericCardContainer";

const ReferralUpdateCard = (props) => {
  const {
    id,
    individual,
    routes,
    meta: { totalReferrals },
  } = props;

  if (totalReferrals < 5) {
    return (
      <GenericCardContainer {...props}>
        Grâce à vous, <strong>{individual?.displayName}</strong> a rejoint{" "}
        <em>Action populaire</em>.
        <br />
        Merci beaucoup, continuez à partager&nbsp;! 👍
      </GenericCardContainer>
    );
  }
  if (totalReferrals === 5) {
    return (
      <GenericCardContainer {...props}>
        5 personnes ont rejoint <em>Action populaire</em> grâce à vous&nbsp;!
        Continuez d'inviter vos amis à partager leur lien personnalisé à leur
        tour&nbsp;!
      </GenericCardContainer>
    );
  }
  if (totalReferrals < 10) {
    return (
      <GenericCardContainer {...props}>
        Encore un&nbsp;! <strong>{individual?.displayName}</strong> a rejoint{" "}
        <em>Action populaire</em>.
        <br />
        C'est super, vous avez fait rejoindre {totalReferrals} personnes&nbsp;!
        Continuez comme ça&nbsp;! 😀
      </GenericCardContainer>
    );
  }
  if (totalReferrals === 10) {
    return (
      <GenericCardContainer {...props}>
        Vous avez convaincu 10 personnes de rejoindre <em>Action populaire</em>
        &nbsp;! Quel est votre secret&nbsp;?!
        <br />
        Si vous n'y aviez pas encore songé, il est peut-être temps de{" "}
        <Link
          href={`/activite/${id}/lien/`}
          params={{ next: routes.createGroup }}
        >
          créer un groupe d'action dans votre ville
        </Link>{" "}
        ;)
      </GenericCardContainer>
    );
  }
  if (totalReferrals === 20) {
    return (
      <GenericCardContainer {...props}>
        Grâce à vous, 20 personnes ont rejoint <em>Action populaire</em>&nbsp;!
        <br />
        Beau travail&nbsp;! Prochaine étape&nbsp;:{" "}
        <Link route="createEvent">organiser un événement en ligne</Link>&nbsp;!
      </GenericCardContainer>
    );
  }
  return (
    <GenericCardContainer {...props}>
      Et de {totalReferrals}&nbsp;! <strong>{individual?.displayName}</strong> a
      rejoint <em>Action populaire</em>. Génial&nbsp;! 😍
    </GenericCardContainer>
  );
};
ReferralUpdateCard.propTypes = {
  id: PropTypes.number.isRequired,
  individual: PropTypes.shape({
    displayName: PropTypes.string,
  }),
  meta: PropTypes.shape({
    totalReferrals: PropTypes.number.isRequired,
  }).isRequired,
  routes: PropTypes.shape({
    createGroup: PropTypes.string,
  }),
};

export default ReferralUpdateCard;
