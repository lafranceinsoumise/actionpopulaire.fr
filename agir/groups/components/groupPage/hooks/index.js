import { useMemo } from "react";

import { useGroup, useGroupSuggestions } from "./group";
import {
  useUpcomingEvents,
  usePastEvents,
  usePastEventReports,
} from "./events";
import { useMessages } from "./messages";

export const useGroupDetail = (groupPk) => {
  const group = useGroup(groupPk);
  const groupSuggestions = useGroupSuggestions(group);
  const upcomingEvents = useUpcomingEvents(group);

  const {
    pastEvents,
    pastEventCount,
    isLoadingPastEvents,
    loadMorePastEvents,
  } = usePastEvents(group);
  const pastEventReports = usePastEventReports(group);
  const { messages, isLoadingMessages, loadMoreMessages } = useMessages(group);

  const allEvents = useMemo(
    () => [...(upcomingEvents || []), ...(pastEvents || [])],
    [upcomingEvents, pastEvents],
  );

  return {
    group,
    groupSuggestions,
    allEvents,
    upcomingEvents,
    pastEvents,
    pastEventCount,
    loadMorePastEvents,
    isLoadingPastEvents,
    pastEventReports,
    messages,
    loadMoreMessages,
    isLoadingMessages,
  };
};
