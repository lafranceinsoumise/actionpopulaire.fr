import React from "react";

import Spacer from "@agir/front/genericComponents/Spacer";

const NewVotingProxyHowTo = () => (
  <div>
    <h2
      css={`
        color: ${(props) => props.theme.primary500};
      `}
    >
      Se porter volontaire pour prendre une procuration
    </h2>
    <Spacer size="1rem" />
    <p>
      Vous êtes disponible les jours de vote et vous souhaitez prendre la
      procuration d'un·e citoyen·ne&nbsp;: merci pour votre aide&nbsp;! Notre
      force est dans le nombre.
    </p>
    <Spacer size="0.5rem" />
    <ol>
      <li>
        <strong>Remplissez ce formulaire</strong> en indiquant vos coordonnées
        et disponibilités
      </li>
      <Spacer size="0.5rem" />
      <li>
        <strong>Vous recevrez un SMS</strong> à valider dès lors qu'un·e
        électeur·ice de votre ville souhaitera porter une procuration
      </li>
      <Spacer size="0.5rem" />
      <li>
        <strong>Vous allez voter en son nom</strong> le jour du scrutin dans son
        bureau de vote
      </li>
    </ol>
  </div>
);

export default NewVotingProxyHowTo;
