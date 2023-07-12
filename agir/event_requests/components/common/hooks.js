import { useMemo } from "react";
import useSWRImmutable from "swr/immutable";

import { getEventRequestEndpoint } from "./api";
import { parseEventSpeakerRequests } from "./utils";

export const useEventSpeaker = () => {
  const { data: speaker, isLoading } = useSWRImmutable(
    getEventRequestEndpoint("getEventSpeaker"),
  );
  const { data: events, isLoading: isLoadingEvents } = useSWRImmutable(
    !!speaker ? getEventRequestEndpoint("getEventSpeakerUpcomingEvents") : null,
  );

  const requests = useMemo(() => parseEventSpeakerRequests(speaker), [speaker]);

  return {
    speaker,
    requests,
    events,
    isLoading,
    isLoadingEvents,
  };
};
