import React from "react";

import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import HomeActions from "./HomeActions";
import HomeExternalLinks from "./HomeExternalLinks";
import HomeFooter from "./HomeFooter";

const StyledHome = styled.main`
  header {
    text-align: center;
    padding: 0 1.5rem 0;

    h2,
    h5 {
      margin: 0;
      padding: 0 0 1.25rem;
    }

    h2 {
      font-size: 2rem;
      line-height: 1;
      font-weight: 700;
      letter-spacing: -0.04em;
      white-space: nowrap;
    }

    h5 {
      font-size: 1rem;
      line-height: 1.5;
      font-weight: 400;
    }

    ${Button} {
      width: 100%;
      justify-content: center;
    }
  }
`;

const Home = () => {
  return (
    <StyledHome>
      <Spacer size="126px" />
      <header>
        <h2>Passez à l'action&nbsp;!</h2>
        <h5>
          Action Populaire est le réseau social d'action de Jean-Luc Mélenchon
          pour l'élection présidentielle de 2022.
        </h5>
        <Button color="primary" as="Link" route="signup">
          S'inscrire
        </Button>
        <Spacer size="11px" />
        <Button color="white" as="Link" route="login">
          Se connecter
        </Button>
      </header>
      <Spacer size="130px" />
      <HomeActions />
      <Spacer size="4rem" />
      <HomeExternalLinks />
      <Spacer size="3.75rem" />
      <HomeFooter />
    </StyledHome>
  );
};

export default Home;
