import React from "react";

export const TABS = {
  ALL: 0,
  GROUPS: 1,
  EVENTS: 2,
};
export const TABS_OPTIONS = [
  {
    id: TABS.ALL,
    label: "Tout",
  },
  {
    id: TABS.GROUPS,
    label: "Groupes",
  },
  {
    id: TABS.EVENTS,
    label: "Événements",
  },
];

export const SORTERS = {
  DATE_ASC: 0,
  DATE_DESC: 1,
  ALPHA_ASC: 2,
  ALPHA_DESC: 3,
};

export const EVENT_TIMES = {
  ALL: 0,
  PAST: 1,
  FUTURE: 2,
};

export const EVENT_TYPES = {
  ALL: 0,
  GROUP_MEETING: "G",
  PUBLIC_MEETING: "M",
  PUBLIC_ACTION: "A",
  OTHER: "O",
};
export const GROUP_TYPES = {
  ALL: 0,
  CERTIFIED: 1,
  NOT_CERTIFIED: 2,
  LOCAL: "L",
  THEMATIC: "B",
  FONCTIONAL: "F",
};

export const EventSort = [
  { label: <>Date &uarr;</>, value: SORTERS.DATE_ASC },
  { label: <>Date &darr;</>, value: SORTERS.DATE_DESC },
  { label: <>Alphabétique &uarr;</>, value: SORTERS.ALPHA_ASC },
  { label: <>Alphabétique &darr;</>, value: SORTERS.ALPHA_DESC },
];
export const EventCategory = [
  { label: "Tous les événements", value: EVENT_TIMES.ALL },
  { label: "Passés", value: EVENT_TIMES.PAST },
  { label: "A venir", value: EVENT_TIMES.FUTURE },
];
export const EventType = [
  { label: "Tous les types", value: EVENT_TYPES.ALL },
  { label: "Réunion privée de groupe", value: EVENT_TYPES.GROUP_MEETING },
  { label: "Événement public", value: EVENT_TYPES.PUBLIC_MEETING },
  { label: "Action publique", value: EVENT_TYPES.PUBLIC_ACTION },
  { label: "Autre", value: EVENT_TYPES.OTHER },
];

export const GroupSort = [
  { label: <>Alphabétique &uarr;</>, value: SORTERS.ALPHA_ASC },
  { label: <>Alphabétique &darr;</>, value: SORTERS.ALPHA_DESC },
];
export const GroupType = [
  { label: "Tous les groupes", value: GROUP_TYPES.ALL },
  { label: "Certifiés", value: GROUP_TYPES.CERTIFIED },
  { label: "Non certifiés", value: GROUP_TYPES.NOT_CERTIFIED },
  { label: "Groupe local", value: GROUP_TYPES.LOCAL },
  { label: "Groupe thématique", value: GROUP_TYPES.THEMATIC },
  { label: "Groupe fonctionnel", value: GROUP_TYPES.FONCTIONAL },
];

export const OPTIONS = {
  EventSort,
  EventCategory,
  EventType,
  GroupSort,
  GroupType,
};
