import useSWR, { mutate } from "swr";
import {
  getUninteracted,
  getUnread,
  setActivityAsDisplayed,
  setActivityAsInteracted,
} from "@agir/activity/common/helpers";
import { useCallback, useEffect } from "react";

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
  const { data } = useSWR("/api/session/");
  const announcement =
    data &&
    Array.isArray(data.announcements) &&
    data.announcements.find((a) => a.customDisplay === slug);

  useEffect(() => {
    if (!announcement) return;
    setActivityAsDisplayed(announcement.activityId);
  }, [announcement]);

  let dismissCallback = useCallback(async () => {
    if (!announcement) {
      return;
    }
    await setActivityAsInteracted(announcement.activityId);

    await mutate("/api/session/", async (session) => ({
      announcements: session.announcements.filter(
        (a) => a.customDisplay !== slug
      ),
      ...session,
    }));
  }, [announcement, slug]);

  return [announcement, dismissCallback];
};
