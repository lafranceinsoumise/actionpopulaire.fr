import querystring from "query-string";
import { simpleInterval } from "@agir/lib/utils/time";
import { routeConfig } from "@agir/front/app/routes.config";

export const GROUP_SELECTION_MAX_LIMIT = 20;
export const TIMINGS = {
  week: {
    value: "week",
    label: "Semaine en cours",
    text: "AGENDA MILITANT DE LA SEMAINE",
  },
  month: {
    value: "month",
    label: "Mois en cours",
    text: "AGENDA MILITANT DU MOIS",
  },
};

export const TIMING_OPTIONS = Object.values(TIMINGS);

export const textifyEvent = (event, _timing, displayZips) => `
${event.subtype.emoji || "🗓️"} ${event.name}
➙ ${simpleInterval(event.startTime, event.endTime)}
➙ Lieu : ${event.location.name}${displayZips ? ` • ${event.location.zip}` : ""}
➙ ${routeConfig.eventDetails.getLink({ eventPk: event.id }, true)}
`;

export const textifyDate = (date, events, timing, displayZips) => `
--- ${date} ---
${events.map((event) => textifyEvent(event, timing, displayZips)).join("")}`;

export const textifiyEvents = (events, timing, displayZips) => `${
  TIMINGS[timing] ? TIMINGS[timing].text : ""
}
${Object.entries(events)
  .map(([date, events]) => textifyDate(date, events, timing, displayZips))
  .join("")}
`;

export const groupUpcomingEventLinkForGroup = (group, absolute = false) => {
  if (!group?.location?.zip) {
    return null;
  }

  const params = {
    d: group.location.departement || undefined,
    z: group.location.zip,
    g: group.id,
  };

  const pathname = routeConfig.groupUpcomingEvents.getLink(undefined, absolute);

  return `${pathname}?${querystring.stringify(params)}`;
};
