import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

/**
 * Énumération à utiliser comme état interne pour les composants chargés de faire des requêtes HTTP
 *
 * L'état IDLE correspond à l'état « normal » du composant, dans lequel il est possible de démarrer une nouvelle
 * requête.
 * L'état LOADING permet d'éviter de dupliquer les requêtes, en désactivant par exemple la validation du formulaire.
 * L'état ERROR permet d'afficher une erreur lié à la requête précédente (et donc de la faire disparaître
 * automatiquement dès la requête suivante).
 */
export const RequestStatus = {
  IDLE: () => ({ loading: false, hasError: false }),
  LOADING: () => ({
    loading: true,
    hasError: false,
  }),
  ERROR: (message) => ({
    loading: false,
    hasError: true,
    message,
  }),
};

/**
 * Les statuts d'élus, tels que rapportés par le backend
 */
export const ELU_STATUTS = {
  DISPONIBLE: "D",
  A_CONTACTER: "A",
  EN_COURS: "E",
  TERMINE: "T",
  PERSONNELLEMENT_VU: "P",
  CC: "C",
};

/**
 * Les infos d'élus telles que transmises par le backend.
 */
export const InfosElu = PropTypes.shape({
  id: PropTypes.number.isRequired,
  nomComplet: PropTypes.string.isRequired,
  titre: PropTypes.string.isRequired,
  sexe: PropTypes.oneOf(["M", "F"]).isRequired,
  pcs: PropTypes.number,
  pcsLabel: PropTypes.string,
  commune: PropTypes.string.isRequired,
  distance: PropTypes.number,
  statut: PropTypes.oneOf(Object.values(ELU_STATUTS)).isRequired,
  parrainageFinal: PropTypes.string,
  idRechercheParrainage: PropTypes.number,
  RechercheParrainages: PropTypes.shape({
    statut: PropTypes.oneOf([2, 3, 4, 5, 6, 7]),
    commentaires: PropTypes.string,
    lienFormulaire: PropTypes.string,
  }),
  mairie: PropTypes.shape({
    adresse: PropTypes.string,
    accessibilite: PropTypes.string,
    detailsAccessibilite: PropTypes.string,
    horaires: PropTypes.array,
    email: PropTypes.string,
    telephone: PropTypes.string,
    site: PropTypes.string,
  }),
});

const statutsConfig = {
  [ELU_STATUTS.DISPONIBLE]: {
    label: "Disponible",
    bg: "primary100",
    text: "primary500",
  },
  [ELU_STATUTS.A_CONTACTER]: {
    label: "À contacter",
    bg: "secondary500",
    text: "text1000",
  },
  [ELU_STATUTS.EN_COURS]: {
    label: "En cours",
    bg: "text100",
    text: "text1000",
  },
  [ELU_STATUTS.TERMINE]: {
    label: "Déjà rencontré",
    bg: "success100",
    text: "text1000",
  },
  [ELU_STATUTS.PERSONNELLEMENT_VU]: {
    label: "Je l'ai vu",
    bg: "success100",
    text: "text1000",
  },
  [ELU_STATUTS.CC]: {
    label: "Reçu par le CC",
    bg: "success500",
    text: "text25",
  },
};

export const ISSUE = {
  ANNULE: 5,
  ENGAGEMENT: 2,
  VALIDE: 3,
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

export const REVERSE_DECISIONS = DECISIONS.filter(
  (d) => d.value !== ISSUE.ENGAGEMENT,
).reduce((acc, d) => Object.assign(acc, { [d.value]: d }), {});

const StatutPillLayout = styled.span`
  display: inline-block;
  color: ${(props) => props.theme[props.text]};
  background-color: ${(props) => props.theme[props.bg]};
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
