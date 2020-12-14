import axios from "@agir/lib/utils/axios";

const debug = require("debug")("agir:helpers");

const bulkUpdateActivityStatusEndpoint = "/api/activity/bulk/update-status/";
const activityEndpoint = "/api/activity/:id/";

export const activityStatus = {
  STATUS_UNDISPLAYED: "U",
  STATUS_DISPLAYED: "S",
  STATUS_INTERACTED: "I",
};

export const requiredActivityTypes = [
  "waiting-payment",
  "group-invitation",
  "new-member",
  "waiting-location-group",
  "group-coorganization-invite",
  "waiting-location-event",
];

export const parseActivities = (data, dismissed = []) => {
  const parsedActivities = {
    required: [],
    unrequired: [],
  };
  if (Array.isArray(data) && data.length > 0) {
    data.forEach((activity) => {
      if (dismissed.includes(activity.id)) {
        return;
      }
      if (requiredActivityTypes.includes(activity.type)) {
        parsedActivities.required.push(activity);
      } else {
        parsedActivities.unrequired.push(activity);
      }
    });
  }
  return parsedActivities;
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

export const dismissActivity = async (
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
    debug.extend("dismissActivity")(e);
    result = false;
  }

  return result;
};

export const setActivitiesAsRead = async (ids = []) => {
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
