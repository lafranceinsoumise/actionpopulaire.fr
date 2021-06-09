import { useCallback } from "react";
import useSWR from "swr";

import {
  setActivityAsInteracted,
  getActivityEndpoint,
} from "@agir/activity/common/api";
import { ACTIVITY_STATUS, getUnread } from "@agir/activity/common/helpers";

export const useHasUnreadActivity = () => {
  const { data: activities } = useSWR(getActivityEndpoint("activities"), {
    revalidateOnMount: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });
  const { data: session } = useSWR(activities ? null : "/api/session/");

  return activities
    ? getUnread(activities).length > 0
    : session && session.hasUnreadActivities;
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
