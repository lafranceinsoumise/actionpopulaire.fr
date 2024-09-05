import React from "react";

import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";

import actImage from "./images/act.jpg";
import meetImage from "./images/meet.jpg";
import organizeImage from "./images/organize.jpg";

const StyledArticle = styled(Link)``;

const StyledActions = styled.main`
  display: grid;
  grid-gap: 3.5rem 2.5rem;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    max-width: 1156px;
    margin: 0 auto;
    grid-template-columns: 1fr 1fr 1fr;
  }

  ${StyledArticle} {
    text-align: center;
    padding: 0 1rem;
    color: ${(props) => props.theme.text1000};

    @media (min-width: ${(props) => props.theme.collapse}px) {
      padding: 0;
    }

    &:hover {
      text-decoration: none;
    }

    & > * {
      margin: 0;
    }

    h4 {
      padding: 1rem 0 0;
      line-height: 1;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        padding-top: 2rem;
      }
    }

    p {
      padding: 0.5rem 0 1rem;
      line-height: 1.5;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        padding-bottom: 1.25rem;
      }
    }
  }
`;

const HomeActions = () => {
  return (
    <StyledActions>
      <StyledArticle route="groupMap">
        <img src={meetImage} height="716" width="424" alt="manifestation" />
        <h4>Rencontrez</h4>
        <p>
          d'autres membres
          <br />
          et agissez ensemble&nbsp;!
        </p>
        <Button color="secondary">Voir les groupes</Button>
      </StyledArticle>
      <StyledArticle route="help">
        <img
          src={actImage}
          height="716"
          width="424"
          alt="distribution de tracts"
        />
        <h4>Agissez concrètement</h4>
        <p>formez-vous et convainquez des gens près de chez vous&nbsp;!</p>
        <Button color="secondary">Lire les fiches pratiques</Button>
      </StyledArticle>
      <StyledArticle route="login">
        <img
          src={organizeImage}
          height="716"
          width="424"
          alt="le premier cahier du programme l'Avenir en Commun"
        />
        <h4>Organisez</h4>
        <p>
          Créez un groupe d'action, commandez du matériel, tracts et
          affiches&nbsp;!
        </p>
        <Button color="secondary">Passer à l'action</Button>
      </StyledArticle>
    </StyledActions>
  );
};

export default HomeActions;
