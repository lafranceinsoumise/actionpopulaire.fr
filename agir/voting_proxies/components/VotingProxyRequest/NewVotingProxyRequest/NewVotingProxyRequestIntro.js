import React from "react";
import styled from "styled-components";

import Spacer from "@agir/front/genericComponents/Spacer";

const NewVotingProxyRequestIntro = () => (
  <div>
    <h2
      css={`
        color: ${(props) => props.theme.primary500};
      `}
    >
      Donner ma procuration
    </h2>
    <Spacer size="1rem" />
    <p>
      Vous souhaitez voter pour Jean-Luc Mélenchon et/ou nos candidat·es aux
      législatives en 2022{" "}
      <strong>
        mais vous ne pourrez pas vous déplacer à votre bureau de vote&nbsp;?
        Faites une procuration&nbsp;!
      </strong>
    </p>
    <Spacer size="0.5rem" />
    <p>
      Le plus pratique reste de demander à un·e proche ou bien à votre voisin·e.
    </p>
    <Spacer size="0.5rem" />
    <p>
      Sinon, remplissez ce formulaire et nous vous mettrons en relation avec
      un·e volontaire disponible pour porter votre procuration et voter à votre
      place.
    </p>
    <Spacer size="1rem" />
    <p
      css={`
        color: ${(props) => props.theme.black500};
        font-size: 0.875rem;
      `}
    >
      ⏱️ Durée du formulaire&nbsp;:&nbsp;1mn
    </p>
  </div>
);

export default NewVotingProxyRequestIntro;
