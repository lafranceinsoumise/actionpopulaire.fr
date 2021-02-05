import { useCallback, useMemo } from "react";
import useSWR, { useSWRInfinite } from "swr";

import logger from "@agir/lib/utils/logger";

import * as api from "@agir/groups/groupPage/api";

const log = logger(__filename);

export const useUpcomingEvents = (group) => {
  const hasUpcomingEvents = group && group.id && group.hasUpcomingEvents;
  const { data, error } = useSWR(
    hasUpcomingEvents
      ? api.getGroupPageEndpoint("getUpcomingEvents", {
          groupPk: group.id,
        })
      : null
  );
  log.debug("Group upcoming events", data);
  return group && group.hasUpcomingEvents && !error ? data : [];
};

export const usePastEvents = (group) => {
  const hasPastEvents = group && group.hasPastEvents;
  const { data, error, size, setSize, isValidating } = useSWRInfinite(
    (pageIndex) =>
      hasPastEvents
        ? api.getGroupPageEndpoint("getPastEvents", {
            groupPk: group.id,
            page: pageIndex + 1,
            pageSize: 3,
          })
        : null
  );
  const pastEvents = useMemo(() => {
    let events = [];
    if (!hasPastEvents || error) {
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
  }, [hasPastEvents, data, error]);
  log.debug("Group past events", pastEvents);

  const pastEventCount = useMemo(() => {
    if (!hasPastEvents || !Array.isArray(data) || !data[0]) {
      return 0;
    }
    return data[0].count;
  }, [hasPastEvents, data]);

  const loadMorePastEvents = useCallback(() => {
    setSize(size + 1);
  }, [setSize, size]);

  const isLoadingPastEvents = hasPastEvents && (!data || isValidating);

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
  const { data, error } = useSWR(
    hasPastEventReports
      ? api.getGroupPageEndpoint("getPastEventReports", {
          groupPk: group.id,
        })
      : null
  );
  log.debug("Group past event reports", data);

  return hasPastEventReports && !error ? data : [];
};
