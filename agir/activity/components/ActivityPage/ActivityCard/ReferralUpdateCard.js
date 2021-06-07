import PropTypes from "prop-types";
import React from "react";

import Link from "@agir/front/app/Link";

import GenericCardContainer from "./GenericCardContainer";

const ReferralUpdateCard = (props) => {
  const {
    individual,
    routes,
    meta: { totalReferrals },
  } = props;

  if (totalReferrals < 5) {
    return (
      <GenericCardContainer {...props}>
        Grâce à vous, <strong>{individual?.displayName}</strong> a parrainé la
        candidature de Jean-Luc Mélenchon.
        <br />
        Merci beaucoup, continuez à partager&nbsp;! 👍
      </GenericCardContainer>
    );
  }
  if (totalReferrals === 5) {
    return (
      <GenericCardContainer {...props}>
        5 personnes ont parrainé la candidature de Jean-Luc Mélenchon grâce à
        vous&nbsp;! La campagne de signature continue, invitez vos amis à
        partager leur lien personnalisé à leur tour&nbsp;!
      </GenericCardContainer>
    );
  }
  if (totalReferrals < 10) {
    return (
      <GenericCardContainer {...props}>
        Encore un&nbsp;! <strong>{individual?.displayName}</strong> a parrainé
        la candidature de Jean-Luc Mélenchon.
        <br />
        C'est super, vous avez fait signer {totalReferrals} personnes&nbsp;!
        Continuez comme ça&nbsp;! 😀
      </GenericCardContainer>
    );
  }
  if (totalReferrals === 10) {
    return (
      <GenericCardContainer {...props}>
        Vous avez permis la signature de 10 personnes&nbsp;! Quel est votre
        secret&nbsp;?!
        <br />
        Si vous n'y aviez pas encore songé, il est peut-être temps de{" "}
        <a href={routes.createGroup}>
          créer une équipe de soutien dans votre ville
        </a>{" "}
        ;)
      </GenericCardContainer>
    );
  }
  if (totalReferrals === 20) {
    return (
      <GenericCardContainer {...props}>
        Grâce à vous, 20 personnes ont parrainé la candidature de Jean-Luc
        Mélenchon&nbsp;!
        <br />
        Beau travail&nbsp;! Prochaine étape&nbsp;:{" "}
        <Link route="createEvent">organiser un événement en ligne</Link> pour
        récolter encore plus de signatures&nbsp;!
      </GenericCardContainer>
    );
  }
  return (
    <GenericCardContainer {...props}>
      Et de {totalReferrals}&nbsp;! <strong>{individual?.displayName}</strong> a
      parrainé la candidature de Jean-Luc Mélenchon. Génial&nbsp;! 😍
    </GenericCardContainer>
  );
};
ReferralUpdateCard.propTypes = {
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
