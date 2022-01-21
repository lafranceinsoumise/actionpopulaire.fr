import React from "react";

export const [TAB_ALL, TAB_GROUPS, TAB_EVENTS] = [0, 1, 2];
export const FILTER_TABS = ["Tout", "Groupes", "Événements"];

export const [DATE_ASC, DATE_DESC, ALPHA_ASC, ALPHA_DESC] = [0, 1, 2, 3];
export const [EVENT_CAT_ALL, EVENT_CAT_PAST, EVENT_CAT_FUTURE] = [0, 1, 2];
export const [
  EVENT_TYPE_ALL,
  EVENT_TYPE_GROUP_MEETING,
  EVENT_TYPE_PUBLIC_MEETING,
  EVENT_TYPE_PUBLIC_ACTION,
  EVENT_TYPE_OTHER,
] = [0, "G", "M", "A", "O"];
export const [
  GROUP_TYPE_ALL,
  GROUP_TYPE_CERTIFIED,
  GROUP_TYPE_NOT_CERTIFIED,
  GROUP_LOCAL,
  GROUP_THEMATIC,
  GROUP_FONCTIONAL,
] = [0, 1, 2, "L", "B", "F"];

export const optionsEventSort = [
  { label: <>Date &uarr;</>, value: DATE_ASC },
  { label: <>Date &darr;</>, value: DATE_DESC },
  { label: <>Alphabétique &uarr;</>, value: ALPHA_ASC },
  { label: <>Alphabétique &darr;</>, value: ALPHA_DESC },
];
export const optionsEventCategory = [
  { label: "Tous les événements", value: EVENT_CAT_ALL },
  { label: "Passés", value: EVENT_CAT_PAST },
  { label: "A venir", value: EVENT_CAT_FUTURE },
];
export const optionsEventType = [
  { label: "Tous les types", value: EVENT_TYPE_ALL },
  { label: "Réunion privée de groupe", value: EVENT_TYPE_GROUP_MEETING },
  { label: "Événement public", value: EVENT_TYPE_PUBLIC_MEETING },
  { label: "Action publique", value: EVENT_TYPE_PUBLIC_ACTION },
  { label: "Autre", value: EVENT_TYPE_OTHER },
];

export const optionsGroupSort = [
  { label: <>Alphabétique &uarr;</>, value: ALPHA_ASC },
  { label: <>Alphabétique &darr;</>, value: ALPHA_DESC },
];
export const optionsGroupType = [
  { label: "Tous les groupes", value: GROUP_TYPE_ALL },
  { label: "Certifiés", value: GROUP_TYPE_CERTIFIED },
  { label: "Non certifiés", value: GROUP_TYPE_NOT_CERTIFIED },
  { label: "Groupe local", value: GROUP_LOCAL },
  { label: "Groupe thématique", value: GROUP_THEMATIC },
  { label: "Groupe fonctionnel", value: GROUP_FONCTIONAL },
];
