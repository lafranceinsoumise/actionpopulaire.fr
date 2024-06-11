import React from "react";

import Spacer from "@agir/front/genericComponents/Spacer";
import ElectionDayWarningBlock from "@agir/voting_proxies/Common/ElectionDayWarningBlock";

const NewVotingProxyRequestIntro = () => (
  <div>
    <ElectionDayWarningBlock />
    <Spacer size="1rem" />
    <h2>Permettre à une personne de voter à ma place</h2>
    <Spacer size="1rem" />
    <p>
      Vous souhaitez voter pour un·e candidate de la France insoumise aux
      élections législatives mais vous serez absent ou dans l'impossibilité de
      vous rendre au bureau de vote les dimanches 30 juin et/ou 7 juillet ?  
      <strong>Faites une procuration !</strong>
    </p>
    <Spacer size="1rem" />
    <p>Le plus simple est de demander à un proche ou bien à un·e voisin·e.</p>
    <Spacer size="1rem" />
    <p>
      Si personne de votre entourage ne peut prendre votre procuration,
      remplissez ce formulaire{" "}
      <strong style={{ boxShadow: "inset 0 -3px 0 0 currentcolor" }}>
        avant le 27 juin pour le premier tour et le 4 juillet pour le second
      </strong>{" "}
      et nous vous mettrons en relation avec une personne disponible pour aller
      voter à votre place avec votre procuration.
    </p>
    <Spacer size="1rem" />
    <p
      css={`
        color: ${({ theme }) => theme.black500};
      `}
    >
      ⏱️ Durée du formulaire&nbsp;:&nbsp;1 minute
    </p>
  </div>
);

export default NewVotingProxyRequestIntro;
