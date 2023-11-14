import React from "react";
import styled from "styled-components";
import useSWRImmutable from "swr/immutable";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import ThematicGroupList from "./ThematicGroupList";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";

const StyledWarning = styled.div`
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1rem;
  padding: 1rem;
  border-radius: ${(props) => props.theme.borderRadius};
  border: 1px solid ${(props) => props.theme.primary150};
  background-color: ${(props) => props.theme.primary50};
  align-items: start;
`;

const StyledPage = styled.main`
  padding: 2rem 0;
  max-width: 70rem;
  margin: 0 auto;
  min-height: 50vh;
  background-color: ${(props) => props.theme.white};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1rem;
    max-width: 100%;
    min-height: calc(100vh - 300px);
  }

  & > header {
    display: flex;
    flex-flow: column nowrap;
    gap: 1.5rem;
    margin-bottom: 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      gap: 1rem;
    }

    & > * {
      flex: 0 0 auto;
    }

    h2 {
      font-size: 1.75rem;
      font-weight: 700;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        font-size: 1.375rem;
      }
    }
  }
`;

const ThematicGroupPage = () => {
  const { data: groups, isLoading } = useSWRImmutable(
    "/api/groupes/thematiques/",
  );

  return (
    <StyledPage>
      <header>
        <h2>Les groupes thématiques de l'espace programme</h2>
        <p>
          Les groupes thématiques de l'espace programme sont issus des travaux
          des livrets pendant la campagne présidentielle. Ils ont été constitués
          pour faire vivre les thèmes initiés en 2017. Aujourd’hui, ces groupes
          continuent de produire du contenu, de réagir à l’actualité et de
          monter des initiatives.
        </p>
        <StyledWarning>
          <RawFeatherIcon name="info" />
          <p>
            Les « livrets de la France insoumise » complètent l’Avenir en
            commun, le programme de la France insoumise.
            <br />
            Les livrets abordent une variété de sujets qui donneront à la France
            son nouveau visage et l’inscriront différemment dans le monde.
            Chaque livret expose les enjeux du sujet et dessine les perspectives
            d’une révolution citoyenne dont notre pays a tant besoin. Chaque
            livret présente aussi les mesures nécessaires pour y arriver. Le
            tout a été chaque fois le fruit d’un travail collectif et coordonné.
            La collection des livrets de la France insoumise est consultable sur{" "}
            <Link route="programme" target="_blank">
              le site du programme
            </Link>
            .
          </p>
        </StyledWarning>
        <p>
          <strong>
            Retrouvez sur cette page les activités des groupes thématiques de
            l'espace programme ainsi que leur adresse de contact. N'hésitez pas
            à leur apporter votre aide !
          </strong>
        </p>
      </header>
      <PageFadeIn ready={!isLoading} wait={<Skeleton />}>
        {!isLoading && <ThematicGroupList groups={groups} />}
      </PageFadeIn>
    </StyledPage>
  );
};

ThematicGroupPage.propTypes = {};

export default ThematicGroupPage;
