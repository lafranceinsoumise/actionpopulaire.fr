import React from "react";

import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledFooter = styled.main`
  padding: 6rem 3.5rem;
  background-color: ${(props) => props.theme.primary500};
  color: ${(props) => props.theme.background0};
  text-align: center;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    flex-flow: row nowrap;
    justify-content: center;
    align-items: center;
  }

  h2 {
    margin: 0;
    font-size: 48px;
    letter-spacing: -0.04em;
    line-height: 1.3;
    font-weight: 700;
    color: inherit;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      flex: 0 0 auto;
    }
  }

  ${Button} {
    width: 100%;
    height: 70px;
    font-size: 1.25rem;
    border: 1px solid ${(props) => props.theme.background0};

    @media (min-width: ${(props) => props.theme.collapse}px) {
      flex: 0 0 200px;
    }
  }
`;

const HomeFooter = () => {
  return (
    <StyledFooter>
      <h2>Passez&nbsp;à l'action&nbsp;!</h2>
      <Spacer size="2rem" />
      <Button link to="/inscription/" color="tertiary">
        S'inscrire
      </Button>
      <Spacer size="1rem" />
      <Button link to="/connexion/" color="primary">
        Se connecter
      </Button>
    </StyledFooter>
  );
};

export default HomeFooter;
