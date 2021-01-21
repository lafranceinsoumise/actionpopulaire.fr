import { useCallback, useMemo } from "react";
import useSWR, { useSWRInfinite } from "swr";

import logger from "@agir/lib/utils/logger";

import MESSAGES from "@agir/groups/groupPage/messages.json";

const log = logger(__filename);

export const useUpcomingEvents = (group) => {
  const hasUpcomingEvents = group && group.hasUpcomingEvents;
  const { data } = useSWR(
    hasUpcomingEvents ? `/api/groupes/${group.id}/evenements/a-venir` : null
  );
  log.debug("Group upcoming events", data);
  return group && group.hasUpcomingEvents ? data : [];
};

export const usePastEvents = (group) => {
  const hasPastEvents = group && group.hasPastEvents;
  const {
    data,
    size: pastEventsSize,
    setSize: setPastEventsSize,
    isValidating: isValidatingPastEvents,
  } = useSWRInfinite((pageIndex) =>
    hasPastEvents
      ? `/api/groupes/${group.id}/evenements/passes?page=${
          pageIndex + 1
        }&page_size=3`
      : null
  );
  const pastEvents = useMemo(() => {
    let events = [];
    if (!hasPastEvents) {
      return events;
    }
    if (!Array.isArray(data)) {
      return events;
    }
    data.forEach(({ results }) => {
      if (Array.isArray(results)) {
        events = events.concat(results);
      }
    });
    return events;
  }, [hasPastEvents, data]);
  log.debug("Group past events", pastEvents);

  const pastEventCount = useMemo(() => {
    if (!hasPastEvents || !Array.isArray(data) || !data[0]) {
      return 0;
    }
    return data[0].count;
  }, [hasPastEvents, data]);

  const loadMorePastEvents = useCallback(() => {
    setPastEventsSize(pastEventsSize + 1);
  }, [setPastEventsSize, pastEventsSize]);

  const isLoadingPastEvents =
    hasPastEvents && (!data || isValidatingPastEvents);

  return {
    pastEvents,
    pastEventCount,
    loadMorePastEvents:
      hasPastEvents && pastEvents && pastEventCount > pastEvents.length
        ? loadMorePastEvents
        : undefined,
    isLoadingPastEvents,
  };
};

export const usePastEventReports = (group) => {
  const hasPastEventReports =
    group && group.isMember && group.hasPastEventReports;
  const { data } = useSWR(
    hasPastEventReports
      ? `/api/groupes/${group.id}/evenements/compte-rendus`
      : null
  );
  log.debug("Group past event reports", data);

  return hasPastEventReports ? data : [];
};

export const useMessages = (group) => {
  const hasMessages = group && group.isMember && group.hasMessages;
  const {
    data: messagesData,
    size: messagesSize,
    setSize: setMessagesSize,
    isValidating: isValidatingMessages,
  } = useSWRInfinite(
    (pageIndex) =>
      hasMessages
        ? `/api/groupes/${group.id}/messages?page=${pageIndex + 1}&page_size=3`
        : null,
    // TEMP: custom fetcher to return fake data
    async (url) =>
      await new Promise((resolve) => {
        setTimeout(() => {
          resolve(
            url ? { count: MESSAGES.length * 2, results: MESSAGES } : undefined
          );
        }, 3000);
      })
  );

  const messages = useMemo(() => {
    let messages = [];
    if (!hasMessages) {
      return messages;
    }
    if (!Array.isArray(messagesData)) {
      return messagesData;
    }
    messagesData.forEach(({ results }) => {
      if (Array.isArray(results)) {
        messages = messages.concat(results);
      }
    });
    return messages;
  }, [hasMessages, messagesData]);
  log.debug("Group messages", messages);

  const messagesCount = useMemo(() => {
    if (!hasMessages || !Array.isArray(messagesData) || !messagesData[0]) {
      return 0;
    }
    return messagesData[0].count;
  }, [hasMessages, messagesData]);
  const loadMoreMessages = useCallback(() => {
    setMessagesSize(messagesSize + 1);
  }, [setMessagesSize, messagesSize]);
  const isLoadingMessages =
    hasMessages && (!messagesData || isValidatingMessages);

  return {
    messages,
    loadMoreMessages:
      hasMessages && messages && messagesCount > messages.length
        ? loadMoreMessages
        : undefined,
    isLoadingMessages,
  };
};

export const useMessage = (group, messagePk) => {
  const hasMessage = group && group.isMember && messagePk;
  const { data } = useSWR(
    hasMessage ? `/api/groupes/${group.id}/messages/${messagePk}` : null,
    // TEMP: custom fetcher to return fake data
    async (url) =>
      await new Promise((resolve) => {
        setTimeout(() => {
          resolve(url ? MESSAGES.find((m) => m.id === messagePk) : undefined);
        }, 3000);
      })
  );
  log.debug("Group message #" + messagePk, data);

  return hasMessage ? data : null;
};

export const useGroup = (groupPk) => {
  const { data } = useSWR(`/api/groupes/${groupPk}`);
  log.debug("Group data", data);

  return data;
};

export const useGroupSuggestions = (group) => {
  const hasSuggestions = group && group.id;
  const { data } = useSWR(
    hasSuggestions ? `/api/groupes/${group.id}/suggestions` : null
  );
  log.debug("Group suggestions", data);

  return hasSuggestions ? data : [];
};

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
    [upcomingEvents, pastEvents]
  );

  const createMessage = console.log;
  const updateMessage = console.log;
  const createComment = console.log;
  const reportMessage = console.log;
  const deleteMessage = console.log;

  return {
    group: group,
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
    createMessage,
    updateMessage,
    createComment,
    reportMessage,
    deleteMessage,
  };
};

export const useGroupMessage = (groupPk, messagePk) => {
  const group = useGroup(groupPk);
  const message = useMessage(group, messagePk);
  const upcomingEvents = useUpcomingEvents(
    group && group.isMember ? group : null
  );
  const { pastEvents, loadMorePastEvents } = usePastEvents(
    group && group.isMember ? group : null
  );

  const updateMessage = console.log;
  const createComment = console.log;
  const reportMessage = console.log;
  const deleteMessage = console.log;
  const isLoading = false;

  const events = useMemo(
    () => [...(upcomingEvents || []), ...(pastEvents || [])],
    [upcomingEvents, pastEvents]
  );

  return {
    group,
    message,
    events,
    loadMoreEvents: loadMorePastEvents,
    updateMessage,
    createComment,
    reportMessage,
    deleteMessage,
    isLoading,
  };
};
