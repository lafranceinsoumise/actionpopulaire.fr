import { mutate } from "swr";

import axios from "@agir/lib/utils/axios";
import logger from "@agir/lib/utils/logger";

import { ACTIVITY_STATUS } from "@agir/activity/common/helpers";

const log = logger(__filename);

export const ENDPOINT = {
  activities: "/api/user/activities/?page=:page&page_size=:pageSize",
  activity: "/api/activity/:activityId/",
  bulkUpdateActivityStatus: "/api/activity/bulk/update-status/",
  announcements: "/api/announcements/",
  customAnnouncement: "/api/user/announcements/custom/:slug/",
  unreadActivityCount: "/api/user/activities/unread-count/",
};

export const getActivityEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const updateActivityStatus = async (
  activityId,
  status = ACTIVITY_STATUS.STATUS_INTERACTED
) => {
  let result = false;
  if (!activityId) {
    return result;
  }
  const url = getActivityEndpoint("activity", { activityId });
  const data = {
    status,
  };
  let res = null;
  try {
    res = await axios.put(url, data);
    result = !!res && res.status === 200;
  } catch (e) {
    log.debug(e);
    result = false;
  }

  return result;
};

export const setActivityAsInteracted = (activityId) =>
  updateActivityStatus(activityId, ACTIVITY_STATUS.STATUS_INTERACTED);

export const setActivityAsDisplayed = (activityId) =>
  updateActivityStatus(activityId, ACTIVITY_STATUS.STATUS_DISPLAYED);

export const setActivitiesAsDisplayed = async (ids = []) => {
  let result = false;
  if (!Array.isArray(ids) || ids.length === 0) {
    return result;
  }
  const url = getActivityEndpoint("bulkUpdateActivityStatus");
  const data = {
    status: ACTIVITY_STATUS.STATUS_DISPLAYED,
    ids,
  };
  let res = null;
  try {
    res = await axios.post(url, data);
    result = !!res && res.status === 204;
  } catch (e) {
    log.debug(e);
    result = false;
  }

  return result;
};

export const setAllActivitiesAsRead = async (ids = []) => {
  const success = await setActivitiesAsDisplayed(ids);
  if (!success) return;

  await mutate("/api/session/", (session) => ({
    ...session,
    hasUnreadActivities: false,
  }));
};
