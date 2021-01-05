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
  group__suggestions: {
    title: "Rejoignez une équipe proche de chez vous",
    body:
      "Les groupes de soutien permettent aux militants de s’organiser dans leur quartier ou dans leur ville. Rejoignez un groupe, agissez sur le terrain et organisez des moments de réflexions politiques !",
    mapIframe: "groupsMap",
  },
  group__creation: {
    title: "Ou bien créez votre équipe !",
    body:
      "Créez votre équipe en quelques clics, et commencez dès aujourd’hui à organiser des actions pour soutenir la candidature de Jean-Luc Mélenchon. Besoin d’inspiration pour animer votre équipe ? Voici quelques pistes.",
    createLabel: "Créer une équipe de soutien",
    createRoute: "createGroup",
  },
  fullGroup__creation: {
    title: "Ou bien animez votre propre équipe et invitez-y vos amis !",
    body: ({ routes }) => [
      <span key="text">
        Créez votre équipe en quelques clics, et commencez dès aujourd’hui à
        organiser des actions pour soutenir la candidature de Jean-Luc
        Mélenchon. Besoin d’inspiration pour animer votre équipe ?{" "}
      </span>,
      routes.newGroupHelp ? (
        <a key="link" href={routes.newGroupHelp}>
          Voici quelques pistes.
        </a>
      ) : null,
    ],
    createLabel: "Créer une équipe de soutien",
    createRoute: "createGroup",
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
    body: (
      <>
        Les groupes thématiques locaux font vivre des thèmes du programme{" "}
        <strong>l’Avenir en Commun</strong> dans un quartier ou une ville.
        Rejoignez un groupe proche de chez vous sur un thème qui vous tient à
        coeur !
      </>
    ),
    createLabel: "Créer un groupe",
    mapLabel: "Voir les groupes dans ma ville",
    mapRoute: "thematicTeams",
    createRoute: "createGroup",
  },
};

const Map = styled.iframe`
  margin: 0;
  padding: 0;
  width: 100%;
  height: 338px;
  border: none;
  overflow: hidden;
`;

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
    mapIframe,
    createLabel,
    createRoute,
  } = ONBOARDING_TYPE[type];
  return (
    <StyledBlock>
      <header>
        {img ? <div style={{ backgroundImage: `url(${img})` }} /> : null}
        {mapIframe && routes[mapIframe] ? (
          <Map src={routes[mapIframe]} />
        ) : null}
        <h3>{title}</h3>
      </header>
      <article>
        <p>{typeof body === "function" ? body(props) : body}</p>
      </article>
      <footer>
        {routes[createRoute] ? (
          <Button as="Link" color="secondary" route={createRoute}>
            {createLabel || "Créer"}
          </Button>
        ) : null}
        {routes[mapRoute] ? (
          <Button as="Link" route={mapRoute}>
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
    newGroupHelp: PropTypes.string,
  }),
};

export default Onboarding;
