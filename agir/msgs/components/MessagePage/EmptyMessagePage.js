import React from "react";
import styled from "styled-components";

import illustration from "@agir/msgs/images/EmptyMessagePageIllustration.svg";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledEmptyPage = styled.main`
  margin: 0 auto;
  text-align: center;
  padding: 187px 0 0;
  max-width: 552px;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 100px 1.5rem 1.5rem;
  }

  & > * {
    margin: 0;
  }

  h2 {
    font-size: 1.5rem;
    color: ${(props) => props.theme.primary500};
    font-weight: 500;
    line-height: 1.4;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.25rem;
    }
  }

  p {
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.6;
    padding-bottom: 2rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      padding-bottom: 1.5rem;
    }
  }
`;

const EmptyMessagePage = () => (
  <StyledEmptyPage>
    <img src={illustration} width="246" height="145" aria-hidden="true" />
    <Spacer size="2.5rem" />
    <h2>Vous n'avez pas encore reçu de messages</h2>
    <Spacer size="1rem" />
    <p>
      Sur Action Populaire, les animateurs de groupe peuvent envoyer des
      messages à leur membres pour organiser l'action.
    </p>
    <Button link color="primary" route="groups">
      Voir les groupes
    </Button>
  </StyledEmptyPage>
);

export default React.memo(EmptyMessagePage);
