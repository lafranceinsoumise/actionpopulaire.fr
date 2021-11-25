import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

export const RequestStatus = {
  IDLE: () => ({ isIdle: true, isLoading: false, isError: false }),
  LOADING: () => ({
    isIdle: false,
    isLoading: true,
    isError: false,
  }),
  ERROR: (message) => ({
    isIdle: false,
    isLoading: false,
    isError: true,
    message,
  }),
};

export const InfosElu = PropTypes.shape({
  id: PropTypes.number,
  nomComplet: PropTypes.string,
  titre: PropTypes.string,
  sexe: PropTypes.oneOf(["M", "F"]),
  commune: PropTypes.string,
  distance: PropTypes.number,
  statut: PropTypes.oneOf(["D", "A", "E", "T", "P"]),
  idRechercheParrainage: PropTypes.number,
  marie: PropTypes.shape({
    adresse: PropTypes.string,
    accessibilite: PropTypes.string,
    detailsAccessibilite: PropTypes.string,
    horaires: PropTypes.object,
    email: PropTypes.string,
    telephone: PropTypes.string,
    site: PropTypes.string,
  }),
});

export const ELU_STATUTS = {
  DISPONIBLE: "D",
  A_CONTACTER: "A",
  EN_COURS: "E",
  TERMINE: "T",
  PERSONNELLEMENT_VU: "P",
};

const statutsConfig = {
  [ELU_STATUTS.DISPONIBLE]: {
    label: "Disponible",
    bg: style.primary100,
    text: style.primary500,
  },
  [ELU_STATUTS.A_CONTACTER]: {
    label: "À contacter",
    bg: style.secondary500,
    text: style.black1000,
  },
  [ELU_STATUTS.EN_COURS]: {
    label: "En cours",
    bg: style.black100,
    text: style.black1000,
  },
  [ELU_STATUTS.TERMINE]: {
    label: "Déjà rencontré",
    bg: style.green100,
    text: style.black1000,
  },
  [ELU_STATUTS.PERSONNELLEMENT_VU]: {
    label: "Je l'ai vu",
    bg: style.green100,
    text: style.black1000,
  },
};

export const ISSUE = {
  ANNULE: 5,
  ENGAGEMENT: 2,
  REFUSE: 4,
  NE_SAIT_PAS: 6,
  AUTRE_ENGAGEMENT: 7,
};

export const DECISIONS = [
  {
    id: "engagement-formulaire",
    label: "S'est engagé à parrainer la candidature et a signé le formulaire",
    formulaire: true,
    commentairesRequis: false,
    value: ISSUE.ENGAGEMENT,
  },
  {
    id: "engagement-sans-formulaire",
    label:
      "S'est engagé à parrainer la candidature et transmettra le formulaire d'engagement par ses propres moyens",
    formulaire: false,
    commentairesRequis: false,
    value: ISSUE.ENGAGEMENT,
  },
  {
    id: "ne-sait-pas",
    label: "Ne s'est pas encore décidé quand à son parrainage",
    formulaire: false,
    commentairesRequis: true,
    commentairesTitre:
      "Indiquer les raisons de son hésitation et sous quels délais il est utile de le recontacter.",
    value: ISSUE.NE_SAIT_PAS,
  },
  {
    id: "autre-candidat",
    label: "S'est engagé ou souhaite soutenir un autre candidat",
    formulaire: false,
    commentairesRequis: true,
    commentairesTitre: "Qui est cet autre candidat ?",
    value: ISSUE.AUTRE_ENGAGEMENT,
  },
  {
    id: "refus",
    label: "Refuse de parrainer la candidature de Jean-Luc Mélenchon",
    formulaire: false,
    commentairesRequis: false,
    value: ISSUE.REFUSE,
  },
];

const StatutPillLayout = styled.span`
  display: inline-block;
  color: ${(props) => props.text};
  background-color: ${(props) => props.bg};
  padding: 0.5rem 1rem;
  border-radius: 7rem;
  font-size: 14px;
  font-weight: 500;
`;

export const StatutPill = ({ statut }) => {
  const statutProps = statutsConfig[statut];
  return (
    <StatutPillLayout {...statutProps}>{statutProps.label}</StatutPillLayout>
  );
};
StatutPill.propTypes = {
  statut: PropTypes.oneOf(Object.keys(statutsConfig)),
};
