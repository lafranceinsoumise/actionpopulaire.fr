import React from "react";

export const TABS = {
  all: {
    id: "all",
    label: "Tout",
    searchPlaceholder: "Rechercher un groupe ou un événement",
    mapRoute: "eventMap",
    hasFilters: false,
    hasEvents: true,
    hasGroups: true,
  },
  groups: {
    id: "groups",
    label: "Groupes",
    searchPlaceholder: "Rechercher un groupe",
    mapRoute: "groupMap",
    hasFilters: "groups",
    hasGroups: true,
    searchType: "groups",
  },
  events: {
    id: "events",
    label: "Événements",
    searchPlaceholder: "Rechercher un événement",
    mapRoute: "eventMap",
    hasFilters: "events",
    hasEvents: true,
    searchType: "events",
  },
};

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
  { label: "Tous les événements", value: null },
  { label: "Passés", value: "PAST" },
  { label: "A venir", value: "UPCOMING" },
];
export const EventType = [
  { label: "Tous les types", value: null },
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
  { label: "Tous les groupes", value: null },
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
