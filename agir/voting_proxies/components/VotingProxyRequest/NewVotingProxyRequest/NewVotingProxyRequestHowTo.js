import React from "react";
import styled from "styled-components";

import Spacer from "@agir/front/genericComponents/Spacer";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledList = styled.ul`
  list-style-type: none;
  padding: 0;

  li {
    display: flex;
    align-items: start;
    gap: 1rem;

    & > :first-child {
      flex: 0 0 auto;
      color: ${(props) => props.theme.primary500};
    }
  }
`;
const NewVotingProxyRequestHowTo = () => (
  <div>
    <h2>Comment ça marche&nbsp;?</h2>
    <Spacer size="1rem" />
    <p>
      La mise en contact pour la procuration est très simple. Vos coordonnées ne
      sont partagées à personne sans votre consentement.
    </p>
    <Spacer size="1rem" />
    <StyledList>
      <li>
        <FeatherIcon name="arrow-right" />
        <span>
          <strong>Remplissez le formulaire.</strong> Vos coordonnées sont
          confidentielles
        </span>
      </li>
      <Spacer size="0.5rem" />
      <li>
        <FeatherIcon name="arrow-right" />
        <span>
          <strong>Vous recevrez un SMS</strong> dès qu'un·e volontaire acceptera
          de prendre votre procuration
        </span>
      </li>
      <Spacer size="0.5rem" />
      <li>
        <FeatherIcon name="arrow-right" />
        <span>
          <strong>Vous prenez contact avec elle</strong> pour rédiger la
          procuration
        </span>
      </li>
      <Spacer size="0.5rem" />
      <li>
        <FeatherIcon name="arrow-right" />
        <span>
          <strong>Vous vous déplacez</strong> au commissariat, à la gendarmerie
          ou au consulat pour établir la procuration et la valider
        </span>
      </li>
    </StyledList>
  </div>
);

export default NewVotingProxyRequestHowTo;
