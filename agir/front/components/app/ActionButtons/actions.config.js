import React from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const ACTIONS = {
  donations: (user) =>
    user?.hasContribution
      ? {
          key: "donations",
          route: "donations",
          label: ["Don", "Faire un don"],
          icon: "heart",
          color: "#FD3D66",
        }
      : {
          key: "donations",
          route: "donationLanding",
          label: ["Don", "Faire un don"],
          icon: "heart",
          color: "#FD3D66",
        },
  contributions: (user) =>
    user?.hasContribution
      ? {
          key: "contributions",
          route: "donations",
          label: ["Don", "Faire un don"],
          icon: "heart",
          color: "#FD3D66",
        }
      : {
          key: "contributions",
          route: "contributions",
          label: ["Financer", "Devenir financeur·euse"],
          icon: "trending-up",
          color: "#FD3D66",
        },
  createEvent: {
    key: "createEvent",
    route: "createEvent",
    label: ["Créer événement", "Créer un événement"],
    color: style.primary500,
    icon: (
      <span style={{ backgroundColor: style.primary500 }}>
        <svg
          width="24"
          height="24"
          viewBox="0 0 16 16"
          fill="none"
          stroke={style.white}
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
    color: style.secondary500,
    textColor: style.black1000,
  },
  createContact: {
    key: "createContact",
    route: "createContact",
    label: ["Ajouter contact", "Ajouter un contact"],
    icon: "user-plus",
    color: "#4D26B9",
  },
  toktokPreview: {
    key: "toktokPreview",
    route: "toktokPreview",
    label: ["Porte-à-porte", "TokTok - Porte-à-porte"],
    icon: (
      <span style={{ backgroundColor: style.PULBleu }}>
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M19.5 21V1.5H4.5V21"
            stroke="white"
            strokeWidth="2.25"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <line
            x1="2.625"
            y1="21.375"
            x2="21.375"
            y2="21.375"
            stroke="white"
            strokeWidth="2.25"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="15" cy="10.5" r="1.5" fill="white" />
        </svg>
      </span>
    ),
    color: style.primary500,
  },
  votingProxy: (user) =>
    user?.votingProxyId
      ? {
          key: "votingProxy",
          route: "acceptedVotingProxyRequests",
          routeParams: { votingProxyPk: user.votingProxyId },
          label: ["Mes procurations", "Mes procurations de vote"],
          icon: "edit-3",
          color: style.votingProxyOrange,
        }
      : {
          key: "votingProxy",
          route: "newVotingProxy",
          label: ["Procuration", "Prendre une procuration"],
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
  newPollingStationOfficer: {
    key: "newPollingStationOfficer",
    route: "newPollingStationOfficer",
    label: ["Assesseurs/délégués", "Devenir assesseur·e ou délégué·e"],
    icon: (
      <span style={{ backgroundColor: style.referralPink }}>
        <svg
          width="25"
          height="24"
          viewBox="0 0 25 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <g clipPath="url(#clip0_5242_40128)">
            <path
              d="M3.5 15H2C1.44772 15 1 15.4477 1 16V21C1 21.5523 1.44772 22 2 22H22C22.5523 22 23 21.5523 23 21V16.5C23 15.9477 22.5523 15.5 22 15.5H20.5M5.5 15.5V3C5.5 2.44772 5.94772 2 6.5 2H17.5C18.0523 2 18.5 2.44771 18.5 3V15.5C18.5 16.0523 18.0523 16.5 17.5 16.5H6.5C5.94772 16.5 5.5 16.0523 5.5 15.5Z"
              stroke="white"
              strokeWidth="2"
            />
            <path
              d="M9 8.6L10.299 10.1588C10.6754 10.6105 11.3585 10.6415 11.7743 10.2257L15 7"
              stroke="white"
              strokeWidth="2"
            />
          </g>
          <defs>
            <clipPath id="clip0_5242_40128">
              <rect
                width="24"
                height="24"
                fill="white"
                transform="translate(0.5)"
              />
            </clipPath>
          </defs>
        </svg>
      </span>
    ),
  },
  help: {
    key: "help",
    route: "help",
    label: ["Aide", "Centre d'aide"],
    icon: "help-circle",
    color: style.black100,
    textColor: style.black1000,
  },
  publicMeetingRequest: {
    key: "publicMeetingRequest",
    route: "publicMeetingRequest",
    label: ["Réunion publique", "Organiser une réunion publique"],
    icon: "radio",
    color: "#00ace0",
  },
  cafePopulaireRequest: {
    key: "cafePopulaireRequest",
    route: "cafePopulaireRequest",
    label: ["Café populaire", "Organiser un café populaire"],
    icon: "coffee",
    color: "#00B171",
  },
};

const DEFAULT_ACTION_ORDER = [
  "donations",
  "createEvent",
  "materiel",
  "createContact",
  "help",
  "actionTools",
];

const GROUP_MANAGER_ACTION_ORDER = [
  "contributions",
  "createEvent",
  "materiel",
  "publicMeetingRequest",
  "cafePopulaireRequest",
  "createContact",
  "help",
  "actionTools",
];

export const getActionsForUser = (user) => {
  let actions = DEFAULT_ACTION_ORDER;

  if (!!user?.groups?.some((group) => group.isManager)) {
    actions = GROUP_MANAGER_ACTION_ORDER;
  }

  return actions
    .map((key) =>
      typeof ACTIONS[key] === "function" ? ACTIONS[key](user) : ACTIONS[key],
    )
    .filter(Boolean);
};

export default ACTIONS;
