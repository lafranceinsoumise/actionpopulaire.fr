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
  statut: PropTypes.oneOf(["D", "A", "E", "T"]),
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
  ACCEPTE: 2,
  REFUSE: 4,
};

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
