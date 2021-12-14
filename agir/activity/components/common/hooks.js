import { useCallback, useEffect, useMemo } from "react";
import useSWR from "swr";
import useSWRInfinite from "swr/infinite";

import {
  setActivityAsInteracted,
  getActivityEndpoint,
} from "@agir/activity/common/api";
import { ACTIVITY_STATUS } from "@agir/activity/common/helpers";

const ACTIVITY_PAGE_SIZE = 10;

export const useActivities = () => {
  const { data, error, mutate, size, setSize, isValidating } = useSWRInfinite(
    (index) =>
      getActivityEndpoint("activities", {
        page: index + 1,
        pageSize: ACTIVITY_PAGE_SIZE,
      })
  );

  const activities = useMemo(() => {
    const activities = {};
    const activityIds = [];
    if (Array.isArray(data)) {
      data.forEach(({ results }) => {
        if (Array.isArray(results)) {
          results.forEach((activity) => {
            if (!activities[activity.id]) {
              activities[activity.id] = activity;
              activityIds.push(activity.id);
            }
          });
        }
      });
    }
    return activityIds.map((id) => activities[id]);
  }, [data]);

  const isLoadingInitialData = !data && !error;

  const isLoadingMore =
    isLoadingInitialData ||
    (size > 0 && data && typeof data[size - 1] === "undefined");

  const activityCount = (data && data[data.length - 1]?.count) || 0;
  const isEmpty = activityCount === 0;
  const isReachingEnd =
    isEmpty ||
    activities.length === activityCount ||
    (data && data[data.length - 1]?.results?.length < ACTIVITY_PAGE_SIZE);
  const isRefreshing = isValidating && data && data.length === size;

  const loadMore = useCallback(() => setSize(size + 1), [setSize, size]);

  return {
    activities,
    error,
    isLoadingInitialData,
    isLoadingMore,
    isRefreshing,
    loadMore: isEmpty || isReachingEnd ? undefined : loadMore,
    mutate,
  };
};

export const useUnreadActivityCount = () => {
  const { data: session } = useSWR("/api/session/");
  const { data, mutate } = useSWR(getActivityEndpoint("unreadActivityCount"), {
    dedupingInterval: 10000,
    focusThrottleInterval: 10000,
  });

  const user = session?.user;

  useEffect(() => {
    typeof user !== "undefined" && mutate();
  }, [user, mutate]);

  return data?.unreadActivityCount || 0;
};

export const useCustomAnnouncement = (slug) => {
  const { data: session } = useSWR("/api/session/");
  const { data, mutate, error } = useSWR(
    session?.user && slug
      ? getActivityEndpoint("customAnnouncement", { slug })
      : null
  );

  const announcement =
    !data?.id || data?.status === ACTIVITY_STATUS.STATUS_INTERACTED
      ? null
      : data;

  const activityId = announcement?.activityId;
  const dismissCallback = useCallback(async () => {
    if (!activityId) {
      return;
    }
    await setActivityAsInteracted(activityId);

    mutate(
      (announcement) => ({
        ...announcement,
        status: ACTIVITY_STATUS.STATUS_INTERACTED,
      }),
      false
    );
  }, [activityId, mutate]);

  return [
    announcement,
    dismissCallback,
    error?.response?.status !== 404 && typeof data === "undefined",
  ];
};
