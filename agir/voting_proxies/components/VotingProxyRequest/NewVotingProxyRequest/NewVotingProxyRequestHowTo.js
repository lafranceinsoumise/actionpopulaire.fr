import React from "react";

import Spacer from "@agir/front/genericComponents/Spacer";

const NewVotingProxyRequestHowTo = () => (
  <div>
    <h2
      css={`
        color: ${(props) => props.theme.primary500};
      `}
    >
      Comment ça marche&nbsp;?
    </h2>
    <Spacer size="1rem" />
    <p>
      La mise en contact pour la procuration est très simple. Vos coordonnées ne
      sont partagées à personne sans votre consentement.
    </p>
    <Spacer size="0.5rem" />
    <ol>
      <li>
        <strong>Remplissez le formulaire.</strong> Vos coordonnées sont
        confidentielles
      </li>
      <Spacer size="0.5rem" />
      <li>
        <strong>Vous recevrez un SMS</strong> dès qu'un·e volontaire acceptera
        de prendre votre procuration
      </li>
      <Spacer size="0.5rem" />
      <li>
        <strong>Vous prenez contact avec elle</strong> pour rédiger la
        procuration
      </li>
      <Spacer size="0.5rem" />
      <li>
        <strong>Vous vous déplacez</strong> au commissariat, à la gendarmerie ou
        au consulat pour établir la procuration et la valider
      </li>
    </ol>
    <Spacer size="1rem" />
    <p
      css={`
        font-size: 0.875rem;
        background-color: ${({ theme }) => theme.primary50};
        padding: 1rem;
        border-radius: ${({ theme }) => theme.borderRadius};
      `}
    >
      Depuis le 1er janvier 2022, vous pouvez désigner un mandataire qui est
      inscrit sur les listes électorales d’une autre commune que vous. Ainsi, si
      vous votez dans la commune A, vous pouvez donner procuration à un·e
      électeur·ice qui vote dans la commune B. En revanche, cette personne devra
      toujours se rendre dans votre bureau de vote le jour du scrutin pour voter
      à votre place.
    </p>
  </div>
);

export default NewVotingProxyRequestHowTo;
