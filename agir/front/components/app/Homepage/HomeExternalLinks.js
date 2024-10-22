import React from "react";

import styled from "styled-components";

import Spacer from "@agir/front/genericComponents/Spacer";

import lfiLogo from "@agir/front/genericComponents/logos/LOGO-LFI_3.png";
import linsoumissionLogo from "@agir/front/genericComponents/logos/linsoumission.svg";
import nfpLogo from "@agir/front/genericComponents/logos/nouveau-front-populaire.png";

const StyledArticle = styled.article`
  padding: 0 1.5rem;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    max-width: 1000px;
    margin: 0 auto;
    text-align: center;
  }

  & > * {
    margin: 0;
  }

  h4 {
    font-size: 1.625rem;
    font-weight: 700;

    &::first-letter {
      text-transform: uppercase;
    }

    span {
      display: none;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        display: inline;
      }
    }
  }

  p {
    font-size: 0.875rem;
    padding: 1rem 0 1.25rem;
    line-height: 1.7;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      padding: 0.5rem 0 1.5rem;
    }
  }

  nav {
    @media (min-width: ${(props) => props.theme.collapse}px) {
      display: flex;
      flex-flow: row nowrap;
      justify-content: space-between;
      align-items: center;
    }

    a {
      display: block;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 5rem;
      border-radius: ${(props) => props.theme.borderRadius};
      border: 1px solid ${(props) => props.theme.text200};
      padding: 0 12px;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        flex: 1 1 270px;
      }

      &:hover {
        border-color: ${(props) => props.theme.text500};
      }
    }
  }
`;

const HomeExternalLinks = () => {
  return (
    <StyledArticle>
      <h4>
        <span>Retrouver</span> l'actualité{" "}
        <span>et les campagnes du mouvement</span>
      </h4>
      <p>
        Action Populaire est le réseau social d’action de la France Insoumise.
        Pour retrouver l’actualité, rendez-vous sur nos sites&nbsp;:
      </p>
      <nav>
        <a href="https://lafranceinsoumise.fr/">
          <img
            src={lfiLogo}
            alt="logo de la France insoumise"
            width="136"
            height="51"
          />
        </a>
        <Spacer size="1rem" />
        <a href="https://www.nouveaufrontpopulaire.fr/">
          <img
            src={nfpLogo}
            alt="logo du Nouveau Front Populaire"
            width="140"
          />
        </a>
        <Spacer size="1rem" />
        <a href="https://linsoumission.fr">
          <img
            src={linsoumissionLogo}
            alt="logo de l'insoumission"
            width="176"
            height="48"
          />
        </a>
      </nav>
    </StyledArticle>
  );
};

export default HomeExternalLinks;
