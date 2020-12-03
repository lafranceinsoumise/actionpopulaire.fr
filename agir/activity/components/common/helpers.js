import axios from "@agir/lib/utils/axios";

const activityEndpoint = "/api/activity/:id";

const activityStatus = {
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

export const dismissActivity = async (id) => {
  let result = false;
  if (!id) {
    return result;
  }
  const url = activityEndpoint.replace(":id", id);
  const data = {
    status: activityStatus.STATUS_INTERACTED,
  };
  let res = null;
  try {
    res = await axios.put(url, data);
    result = !!res && res.status === 200;
  } catch (e) {
    console.log(e);
    result = false;
  }

  return result;
};
