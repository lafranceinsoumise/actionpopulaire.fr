import { DateTime, Interval } from "luxon";

export const EVENT_DEFAULT_DURATIONS = [
  {
    value: 60,
    label: "1h",
  },
  {
    value: 90,
    label: "1h30",
  },
  {
    value: 120,
    label: "2h",
  },
  {
    value: 180,
    label: "3h",
  },
  {
    value: null,
    label: "Personnalisée",
  },
];

export const EVENT_TYPES = {
  G: {
    label: "Réunion de groupe",
    description:
      "Une réunion qui concerne principalement les membres du groupes, et non le public de façon générale. Par exemple, la réunion hebdomadaire du groupe, une réunion de travail, ou l'audition d'une association",
  },
  M: {
    label: "Événement public",
    description:
      "Un événement ouvert à tous les publics, au-delà des membres du groupe, mais qui aura lieu dans un lieu privé. Par exemple, un événement public avec un orateur, une projection ou un concert",
  },
  A: {
    label: "Action publique",
    description:
      "Une action qui se déroulera dans un lieu public et qui aura comme objectif principal  d'aller à la rencontre ou d'atteindre des personnes extérieures à la France insoumise",
  },
  O: {
    label: "Autre",
    description:
      "Tout autre type d'événement qui ne rentre pas dans les autres catégories",
  },
};

export const formatEvent = (event) => {
  if (!event) {
    return null;
  }

  if (!event.startTime || !event.endTime) {
    return event;
  }

  try {
    const startDateTime = DateTime.fromJSDate(
      new Date(event.startTime)
    ).setLocale("fr");
    const endDateTime = DateTime.fromJSDate(new Date(event.endTime)).setLocale(
      "fr"
    );
    return {
      ...event,
      schedule: Interval.fromDateTimes(startDateTime, endDateTime),
    };
  } catch (e) {
    return event;
  }
};
