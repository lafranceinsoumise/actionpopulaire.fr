import { useMemo } from "react";

import { useGroup, useGroupSuggestions } from "./group";
import {
  useUpcomingEvents,
  usePastEvents,
  usePastEventReports,
} from "./events";
import { useMessages, useMessage } from "./messages";

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

export const useGroupMessage = (groupPk, messagePk) => {
  const group = useGroup(groupPk);
  const upcomingEvents = useUpcomingEvents(
    group && group.isMember ? group : null,
  );
  const { pastEvents, loadMorePastEvents: loadMoreEvents } = usePastEvents(
    group && group.isMember ? group : null,
  );

  const { message, isLoading } = useMessage(group, messagePk);

  const events = useMemo(
    () => [...(upcomingEvents || []), ...(pastEvents || [])],
    [upcomingEvents, pastEvents],
  );

  return {
    group,
    message,
    events,
    loadMoreEvents,
    isLoading,
  };
};
