import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";

import style from "@agir/front/genericComponents/_variables.scss";

import onboardingActionImage from "./images/onboarding__action.png";
import onboardingThematicImage from "./images/onboarding__thematic.png";

const ONBOARDING_TYPE = {
  action: {
    img: onboardingActionImage,
    title:
      "Rejoignez un groupe d’action de votre ville pour militer localement",
    body:
      "Les groupes d’actions permettent aux militants de s’organiser dans leur quartier ou dans leur ville. Rejoignez un groupe, agissez sur le terrain et organisez des moments de réflexions politiques !",
    href: "https://lafranceinsoumise.fr/groupes-action/carte-groupes/",
  },
  thematic: {
    img: onboardingThematicImage,
    title: "Rejoignez un groupe thématique local",
    body:
      "Les groupes thématiques locaux font vivre des thèmes du programme <a href='' rel='noopener noreferrer' target='_blank'>l’Avenir en Commun</a> dans un quartier ou une ville. Rejoignez un groupe proche de chez vous sur un thème qui vous tient à coeur !",
    href: "http://agir.local:8000/equipes-thematiques/",
  },
};

const StyledBlock = styled.section`
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  justify-content: space-between;
  padding: 0;

  @media (max-width: ${style.collapse}px) {
    padding: 0 25px;
  }

  & + & {
    margin-top: 60px;
  }

  header {
    div {
      display: block;
      margin-bottom: 28px;
      width: 100%;
      height: 233px;
      background-repeat: no-repeat;
      background-position: center center;
      background-size: cover;
      border-radius: 8px;

      @media (max-width: ${style.collapse}px) {
        height: 138px;
        margin-bottom: 24px;
      }
    }
  }

  article {
    margin: 0 0 24px;

    a {
      font-weight: 700;
      text-decoration: underline;
    }
  }

  footer {
    display: flex;
    flex-direction: row;

    @media (max-width: ${style.collapse}px) {
      flex-direction: column;
      align-items: flex-start;
    }

    ${Button} {
      @media (min-width: ${style.collapse}px) {
        margin-right: 11px;
      }
      @media (max-width: ${style.collapse}px) {
        margin-bottom: 11px;
      }
    }
  }
`;

const GroupOnboarding = (props) => {
  const { type, routes } = props;
  if (!type || !ONBOARDING_TYPE[type]) {
    return null;
  }
  const { img, title, body, href } = ONBOARDING_TYPE[type];
  return (
    <StyledBlock>
      <header>
        <div style={{ backgroundImage: `url(${img})` }} />
        <h3>{title}</h3>
      </header>
      <article>
        <p dangerouslySetInnerHTML={{ __html: body }} />
      </article>
      <footer>
        <Button as="a" href={href} color="primary">
          Voir les groupes dans ma ville
        </Button>
        <Button as="a" href={routes.createGroup}>
          Créer un groupe
        </Button>
      </footer>
    </StyledBlock>
  );
};

GroupOnboarding.propTypes = {
  type: PropTypes.oneOf(Object.keys(ONBOARDING_TYPE)),
  routes: PropTypes.shape({
    createGroup: PropTypes.string,
  }),
};

export default GroupOnboarding;
