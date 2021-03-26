import React, { useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import HomeActions from "./HomeActions";
import HomeExternalLinks from "./HomeExternalLinks";
import HomeFooter from "./HomeFooter";

const StyledMap = styled.iframe`
  display: block;
  padding: 0;
  margin: -242px auto 0;
  width: 100%;
  max-width: 1156px;
  height: 542px;
  border: none;
  overflow: hidden;
  background-color: #aad3df;
`;

const StyledHome = styled.main`
  header {
    text-align: center;
    padding: 0 1.5rem 0;
    height: 676px;
    background-color: ${style.secondary500};
    padding: 82px 0;

    h2,
    h5 {
      margin: 0;
      padding: 0;
    }

    h2 {
      font-size: 66px;
      line-height: 1.5;
      font-weight: 700;
      letter-spacing: -0.04em;
      white-space: nowrap;
    }

    h5 {
      font-size: 1.25rem;
      line-height: 1.5;
      font-weight: normal;
      max-width: 580px;
      margin: 0 auto;
      padding-bottom: 2.25rem;
    }

    div {
      display: flex;
      justify-content: center;

      & > * {
        flex: 0 0 auto;
      }

      ${Button} {
        width: auto;
        justify-content: center;
        height: 70px;
        font-size: 1.25rem;
        margin: 0;
      }
    }
  }
`;

const Home = () => {
  const routes = useSelector(getRoutes);

  const [isLoaded, setIsLoaded] = useState(false);

  return (
    <StyledHome>
      <header>
        <h2>Passez à l'action&nbsp;!</h2>
        <h5>
          Agissez concrètement dans votre quartier et faites gagner Jean-Luc
          Mélenchon en 2022 !
        </h5>
        <div>
          <Button color="primary" as="Link" route="signup">
            Je crée mon compte
          </Button>
          <Spacer size="1rem" />
          <Button color="white" as="Link" route="login">
            Je me connecte
          </Button>
        </div>
      </header>
      {routes && routes.eventsMap && (
        <StyledMap
          $isLoaded={isLoaded}
          src={routes.eventsMap + "?no_controls=1"}
          onLoad={() => setIsLoaded(true)}
        />
      )}
      <Spacer size="4rem" />
      <HomeActions />
      <Spacer size="5.25rem" />
      <HomeExternalLinks />
      <Spacer size="5.25rem" />
      <HomeFooter />
    </StyledHome>
  );
};

export default Home;
