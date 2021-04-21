import useSWR, { mutate } from "swr";
import {
  getUninteracted,
  getUnread,
  setActivityAsDisplayed,
  setActivityAsInteracted,
} from "@agir/activity/common/helpers";
import { useCallback, useEffect, useMemo, useRef } from "react";

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

  const announcementStatus = useRef(0);
  const announcement = useMemo(
    () =>
      data && Array.isArray(data.announcements)
        ? data.announcements.find((a) => a.customDisplay === slug)
        : null,
    [slug, data]
  );

  useEffect(() => {
    if (announcement && announcementStatus.current === 0) {
      announcementStatus.current = 1;
      setActivityAsDisplayed(announcement.activityId);
    }
  }, [announcement]);

  let dismissCallback = useCallback(async () => {
    if (!announcement) {
      return;
    }
    announcementStatus.current = 2;
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
