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
  DATE_ASC: "DATE_ASC",
  DATE_DESC: "DATE_DESC",
  ALPHA_ASC: "ALPHA_ASC",
  ALPHA_DESC: "ALPHA_DESC",
};

export const EventSort = [
  { label: <>Date &uarr;</>, value: SORTERS.DATE_ASC },
  { label: <>Date &darr;</>, value: SORTERS.DATE_DESC },
  { label: <>Alphabétique &uarr;</>, value: SORTERS.ALPHA_ASC },
  { label: <>Alphabétique &darr;</>, value: SORTERS.ALPHA_DESC },
];
export const EventCategory = [
  { label: "Tous les événements", value: 0 },
  { label: "Passés", value: "PAST" },
  { label: "A venir", value: "FUTURE" },
];
export const EventType = [
  { label: "Tous les types", value: 0 },
  { label: "Réunion privée de groupe", value: "G" },
  { label: "Événement public", value: "M" },
  { label: "Action publique", value: "A" },
  { label: "Autre", value: "O" },
];

export const GroupSort = [
  { label: <>Alphabétique &uarr;</>, value: SORTERS.ALPHA_ASC },
  { label: <>Alphabétique &darr;</>, value: SORTERS.ALPHA_DESC },
];
export const GroupType = [
  { label: "Tous les groupes", value: 0 },
  { label: "Certifiés", value: "CERTIFIED" },
  { label: "Non certifiés", value: "NOT_CERTIFIED" },
  { label: "Groupe local", value: "L" },
  { label: "Groupe thématique", value: "B" },
  { label: "Groupe fonctionnel", value: "F" },
];

export const OPTIONS = {
  EventSort,
  EventCategory,
  EventType,
  GroupSort,
  GroupType,
};
