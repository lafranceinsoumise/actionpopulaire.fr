import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";

import style from "@agir/front/genericComponents/_variables.scss";

import onboardingEventImage from "./images/onboarding__event.jpg";
import onboardingActionImage from "./images/onboarding__action.jpg";
import onboardingThematicImage from "./images/onboarding__thematic.jpg";

const ONBOARDING_TYPE = {
  event: {
    img: onboardingEventImage,
    title: "Organisez un événement près de chez vous !",
    body:
      "Agissez et organisez un événement de soutien, tel qu’une action de solidarité, une réunion en ligne pour discuter du programme, une écoute collective des futurs meetings... Organisez-vous avec d’autres membres pour soutenir la campagne !",
    createLabel: "Créer un événement",
    createRoute: "createEvent",
  },
  group__nsp: {
    img: onboardingActionImage,
    title: "Rejoignez ou organisez une équipe de soutien",
    body:
      "Les équipes de soutien permettent aux militants de s’organiser dans leur quartier ou dans leur ville. Rejoignez un groupe, agissez sur le terrain et organisez des moments de réflexions politiques !",
    createLabel: "Créer une équipe",
    mapLabel: "Voir les équipes dans ma ville",
    mapRoute: "groupMapPage",
    createRoute: "createGroup",
  },
  group__action: {
    img: onboardingActionImage,
    title:
      "Rejoignez un groupe d’action de votre ville pour militer localement",
    body:
      "Les groupes d’actions permettent aux militants de s’organiser dans leur quartier ou dans leur ville. Rejoignez un groupe, agissez sur le terrain et organisez des moments de réflexions politiques !",
    createLabel: "Créer un groupe",
    mapLabel: "Voir les groupes dans ma ville",
    mapRoute: "groupMapPage",
    createRoute: "createGroup",
  },
  group__thematic: {
    img: onboardingThematicImage,
    title: "Rejoignez un groupe thématique local",
    body:
      "Les groupes thématiques locaux font vivre des thèmes du programme <a href='' rel='noopener noreferrer' target='_blank'>l’Avenir en Commun</a> dans un quartier ou une ville. Rejoignez un groupe proche de chez vous sur un thème qui vous tient à coeur !",
    createLabel: "Créer un groupe",
    mapLabel: "Voir les groupes dans ma ville",
    mapRoute: "thematicTeams",
    createRoute: "createGroup",
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

const Onboarding = (props) => {
  const { type, routes } = props;
  if (!type || !ONBOARDING_TYPE[type]) {
    return null;
  }
  const {
    img,
    title,
    body,
    mapLabel,
    mapRoute,
    createLabel,
    createRoute,
  } = ONBOARDING_TYPE[type];
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
        {routes[createRoute] ? (
          <Button as="a" color="secondary" href={routes[createRoute]}>
            {createLabel || "Créer"}
          </Button>
        ) : null}
        {routes[mapRoute] ? (
          <Button as="a" href={routes[mapRoute]}>
            {mapLabel || "Voir la carte"}
          </Button>
        ) : null}
      </footer>
    </StyledBlock>
  );
};

Onboarding.propTypes = {
  type: PropTypes.oneOf(Object.keys(ONBOARDING_TYPE)),
  routes: PropTypes.shape({
    createGroup: PropTypes.string,
  }),
};

export default Onboarding;
