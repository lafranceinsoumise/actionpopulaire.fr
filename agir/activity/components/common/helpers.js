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
