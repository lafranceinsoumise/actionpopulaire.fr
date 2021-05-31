import useSWR from "swr";
import {
  activityStatus,
  getUninteracted,
  getUnread,
  setActivityAsInteracted,
} from "@agir/activity/common/helpers";
import { useCallback, useMemo } from "react";

export const useHasUnreadActivity = () => {
  const { data: activities } = useSWR("/api/user/activities/", {
    revalidateOnMount: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });

  const { data: session } = useSWR(activities ? null : "/api/session/");

  return activities
    ? getUnread(activities).length > 0
    : session && session.hasUnreadActivities;
};

export const useRequiredActivityCount = () => {
  const { data: activities } = useSWR("/api/user/required-activities/", {
    revalidateOnMount: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });

  const { data: session } = useSWR(activities ? null : "/api/session/");

  return activities
    ? getUninteracted(activities).length
    : session && session.requiredActionActivitiesCount;
};

export const useCustomAnnouncement = (slug) => {
  const { data: session } = useSWR("/api/session/");
  const { data, mutate } = useSWR(
    session?.user && slug ? `/api/user/announcements/custom/${slug}/` : null
  );

  const announcementId = data?.id;
  const announcement = useMemo(
    () => {
      if (
        !announcementId ||
        data?.status === activityStatus.STATUS_INTERACTED
      ) {
        return null;
      }
      return data;
    },
    //eslint-disable-next-line
    [announcementId]
  );

  const activityId = announcement?.activityId;
  const dismissCallback = useCallback(async () => {
    if (!activityId) {
      return;
    }
    await setActivityAsInteracted(activityId);

    mutate(
      (announcement) => ({
        ...announcement,
        status: activityStatus.STATUS_INTERACTED,
      }),
      false
    );
  }, [activityId, mutate]);

  return [announcement, dismissCallback, typeof data === "undefined"];
};
