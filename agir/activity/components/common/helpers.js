export const ACTIVITY_STATUS = {
  STATUS_UNDISPLAYED: "U",
  STATUS_DISPLAYED: "S",
  STATUS_INTERACTED: "I",
};

export const CHANGED_DATA_LABEL = {
  name: "nom",
  start_time: "date",
  end_time: "date",
  contact_name: "contact",
  contact_email: "contact",
  contact_phone: "contact",
  location_name: "lieu",
  location_address1: "lieu",
  location_address2: "lieu",
  location_city: "lieu",
  location_zip: "lieu",
  location_country: "lieu",
  description: "présentation",
  facebook: "lien facebook",
};

export const getUnread = (data) => {
  return Array.isArray(data)
    ? data.filter(
        (activity) => activity.status === ACTIVITY_STATUS.STATUS_UNDISPLAYED,
      )
    : [];
};

export const getUnreadCount = (data) => {
  return getUnread(data).length;
};

export const getUninteracted = (data) => {
  return Array.isArray(data)
    ? data.filter(
        (activity) => activity.status !== ACTIVITY_STATUS.STATUS_INTERACTED,
      )
    : [];
};

export const getUninteractedCount = (data) => {
  return getUninteracted(data).length;
};
