import React from "react";

import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";

import actImage from "./images/act.jpg";
import meetImage from "./images/meet.jpg";
import organizeImage from "./images/organize.jpg";

const StyledArticle = styled.article``;

const StyledActions = styled.main`
  display: grid;
  grid-gap: 3.5rem 2.5rem;

  @media (min-width: ${style.collapse}px) {
    max-width: 1156px;
    margin: 0 auto;
    grid-template-columns: 1fr 1fr 1fr;
  }

  ${StyledArticle} {
    text-align: center;
    padding: 0 1rem;

    @media (min-width: ${style.collapse}px) {
      padding: 0;
    }

    & > * {
      margin: 0;
    }

    h4 {
      padding: 1rem 0 0;
      line-height: 1;

      @media (min-width: ${style.collapse}px) {
        padding-top: 2rem;
      }
    }

    p {
      padding: 0.5rem 0 1rem;
      line-height: 1.5;

      @media (min-width: ${style.collapse}px) {
        padding-bottom: 1.25rem;
      }
    }
  }
`;

const HomeActions = () => {
  return (
    <StyledActions>
      <StyledArticle>
        <img src={meetImage} alt="manifestation" />
        <h4>Rencontrez</h4>
        <p>
          d'autres membres
          <br />
          et agissez ensemble&nbsp;!
        </p>
        <Button color="secondary" as="Link" route="groupMapPage">
          Voir les groupes
        </Button>
      </StyledArticle>
      <StyledArticle>
        <img src={actImage} alt="distribution de tracts" />
        <h4>Agissez concrètement</h4>
        <p>formez-vous et convainquez des gens près de chez vous&nbsp;!</p>
        <Button
          color="secondary"
          as="Link"
          href="https://infos.actionpopulaire.fr/"
        >
          Lisez les fiches pratiques
        </Button>
      </StyledArticle>
      <StyledArticle>
        <img
          src={organizeImage}
          alt="le premier cahier du programme l'Avenir en Commun"
        />
        <h4>Organisez</h4>
        <p>
          Créez une équipe de soutien, commandez du matériel, tracts et
          affiches&nbsp;!
        </p>
        <Button color="secondary" as="Link" to="/connexion/">
          Passez à l'action
        </Button>
      </StyledArticle>
    </StyledActions>
  );
};

export default HomeActions;
