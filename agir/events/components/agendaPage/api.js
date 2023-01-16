import { useEffect, useState } from "react";
import useSWR from "swr";
import useSWRImmutable from "swr/immutable";

export const EVENT_TYPES = {
  nearEvents: "suggestions pour moi",
  groupEvents: "dans mes groupes",
  ongoingEvents: "en cours",
  pastEvents: "passés",
  organizedEvents: "organisés",
};

const ENDPOINT = {
  rsvpedEvents: "/api/evenements/rsvped/",
  nearEvents: "/api/evenements/suggestions/",
  groupEvents: "/api/evenements/mes-groupes/",
  ongoingEvents: "/api/evenements/rsvped/en-cours/",
  pastEvents: "/api/evenements/rsvped/passes/",
  organizedEvents: "/api/evenements/organises/",
  grandEvents: "/api/evenements/grands-evenements/",
};

export const getAgendaEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const useEventSuggestions = (isPaused = false) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeKey = Object.keys(EVENT_TYPES)[activeIndex];
  const { data: session } = useSWRImmutable("/api/session/");
  const { data: events, mutate } = useSWR(
    activeKey && getAgendaEndpoint(activeKey),
    { isPaused }
  );

  const userID = session?.user && session.user.id;
  const userZip = session?.user && session.user.zip;

  useEffect(() => {
    userID && userZip && mutate();
  }, [userID, userZip, mutate]);

  return [
    Object.values(EVENT_TYPES),
    activeIndex,
    setActiveIndex,
    events,
    activeKey,
  ];
};
