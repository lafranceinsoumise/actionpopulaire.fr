import React from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const ACTIONS = {
  /*
  groups: {
    key: "groups",
    route: "groups",
    label: "Carte",
    icon: "map",
    color: style.black700,
  },
  */
  donations: {
    key: "donations",
    route: "donations",
    label: ["Don", "Faire un don"],
    icon: "heart",
    color: style.redNSP,
  },
  createEvent: {
    key: "createEvent",
    route: "createEvent",
    label: ["Créer événement", "Créer un événement"],
    color: style.secondary500,
    icon: (
      <span style={{ backgroundColor: style.secondary500 }}>
        <svg
          width="24"
          height="24"
          viewBox="0 0 16 16"
          fill="none"
          stroke="#000A2C"
          strokeWidth={1.33}
          strokeLinecap="round"
          strokeLinejoin="round"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M14 8.99999V3.99999C14 3.26361 13.403 2.66666 12.6667 2.66666H3.33333C2.59695 2.66666 2 3.26361 2 3.99999V13.3333C2 14.0697 2.59695 14.6667 3.33333 14.6667H8.66667" />
          <path d="M10.6667 1.33334V4.00001" />
          <path d="M5.33331 1.33334V4.00001" />
          <path d="M2 6.66666H14" />
          <path d="M12.6667 11.3333V15.3333" />
          <path d="M14.6667 13.3333H10.6667" />
        </svg>
      </span>
    ),
  },
  coupDeFil: {
    key: "coupDeFil",
    route: "coupDeFil",
    label: ["Coup de fil", "Coup de fil pour convaincre"],
    icon: "phone",
    color: style.green500,
  },
  materiel: {
    key: "materiel",
    route: "materiel",
    label: "Matériel",
    icon: "shopping-bag",
    color: style.materielBlue,
  },
  createContact: {
    key: "createContact",
    route: "createContact",
    label: ["Ajouter contact", "Ajouter un contact"],
    icon: "user-plus",
    color: style.primary500,
  },
  referralSearch: {
    key: "referralSearch",
    route: "referralSearch",
    label: "500 parrainages",
    icon: "pen-tool",
    color: style.referralPink,
  },
  votingProxy: {
    key: "votingProxy",
    route: "newVotingProxy",
    label: "Prendre une procuration",
    icon: "edit-3",
    color: style.votingProxyOrange,
  },
  actionTools: {
    key: "actionTools",
    route: "actionTools",
    label: "Voir tout",
    icon: (
      <RawFeatherIcon
        style={{
          backgroundColor: "transparent",
          border: `1px solid ${style.black200}`,
          color: style.black1000,
        }}
        name="arrow-right"
      />
    ),
  },
};

const DEFAULT_ACTION_ORDER = [
  "groups",
  "donations",
  "createEvent",
  "coupDeFil",
  "materiel",
  "createContact",
  "referralSearch",
  "votingProxy",
  "actionTools",
];
const GROUP_MANAGER_ACTION_ORDER = [
  "createEvent",
  "materiel",
  "createContact",
  "coupDeFil",
  "donations",
  "referralSearch",
  "groups",
  "votingProxy",
  "actionTools",
];

export const getActionsForUser = (user) => {
  let actions = DEFAULT_ACTION_ORDER;

  if (!!user?.groups?.some((group) => group.isManager)) {
    actions = GROUP_MANAGER_ACTION_ORDER;
  }

  return actions.map((key) => ACTIONS[key]).filter(Boolean);
};

export default ACTIONS;
