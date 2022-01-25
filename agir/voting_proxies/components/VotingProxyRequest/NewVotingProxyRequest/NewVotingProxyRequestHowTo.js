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
        <strong>Vous recevrez un SMS</strong> dès qu'un·e citoyen·ne acceptera
        de prendre votre procuration
      </li>
      <Spacer size="0.5rem" />
      <li>
        <strong>Vous prenez contact avec elle</strong> pour rédiger la
        procuration
      </li>
    </ol>
  </div>
);

export default NewVotingProxyRequestHowTo;
