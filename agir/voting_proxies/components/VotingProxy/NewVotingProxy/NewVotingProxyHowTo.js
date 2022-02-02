import React from "react";

import Link from "@agir/front/app/Link";
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
        électeur·ice proche de chez vous souhaitera porter une procuration
      </li>
      <Spacer size="0.5rem" />
      <li>
        <strong>Vous allez voter en son nom</strong> le jour du scrutin dans son
        bureau de vote
      </li>
    </ol>
    <Spacer size="1rem" />
    <p>
      <em>
        Vous ne vous pouvez pas vous déplacer le 10 et/ou 24 avril&nbsp;?{" "}
        <Link route="newVotingProxyRequest">
          Permettez à quelqu'un de voter à votre place
        </Link>
        .
      </em>
    </p>
    <Spacer size="1rem" />
    <p
      css={`
        font-size: 0.875rem;
        background-color: ${({ theme }) => theme.primary50};
        padding: 1rem;
        border-radius: ${({ theme }) => theme.borderRadius};
      `}
    >
      Depuis le 1er janvier 2022, il est possible de voter pour une personne
      inscrite sur les listes électorales d'une autre commune.
      <br />
      Ainsi, si vous votez dans la commune A, vous pourrez voter pour un·e
      électeur·ice qui vote dans la commune B - en revanche, vous devrez
      toujours vous rendre dans son bureau de vote le jour du scrutin.
      <br />
      <br />
      Ainsi, pour vous mettre en contact avec des électeur·ices, nous
      privilégierons votre adresse actuelle, si celle-ci est différente de votre
      commune d'inscription.
    </p>
  </div>
);

export default NewVotingProxyHowTo;
