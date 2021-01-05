import axios from "@agir/lib/utils/axios";

import logger from "@agir/lib/utils/logger";
const log = logger(__filename);

const bulkUpdateActivityStatusEndpoint = "/api/activity/bulk/update-status/";
const activityEndpoint = "/api/activity/:id/";

export const activityStatus = {
  STATUS_UNDISPLAYED: "U",
  STATUS_DISPLAYED: "S",
  STATUS_INTERACTED: "I",
};

export const getUnread = (data) => {
  return Array.isArray(data)
    ? data.filter(
        (activity) => activity.status === activityStatus.STATUS_UNDISPLAYED
      )
    : [];
};

export const getUnreadCount = (data) => {
  return getUnread(data).length;
};

export const updateActivityStatus = async (
  id,
  status = activityStatus.STATUS_INTERACTED
) => {
  let result = false;
  if (!id) {
    return result;
  }
  const url = activityEndpoint.replace(":id", id);
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

export const setActivityAsInteracted = (id) =>
  updateActivityStatus(id, activityStatus.STATUS_INTERACTED);

export const setActivityAsDisplayed = (id) =>
  updateActivityStatus(id, activityStatus.STATUS_DISPLAYED);

export const setActivitiesAsDisplayed = async (ids = []) => {
  let result = false;
  if (!Array.isArray(ids) || ids.length === 0) {
    return result;
  }
  const url = bulkUpdateActivityStatusEndpoint;
  const data = {
    status: activityStatus.STATUS_DISPLAYED,
    ids,
  };
  let res = null;
  try {
    res = await axios.post(url, data);
    result = !!res && res.status === 204;
  } catch (e) {
    console.log(e);
    result = false;
  }

  return result;
};
