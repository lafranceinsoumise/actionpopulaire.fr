import {
  activityStatus,
  setActivitiesAsDisplayed,
  setActivityAsDisplayed,
  setActivityAsInteracted,
} from "@agir/activity/common/helpers";
import { mutate } from "swr";

export const setAllActivitiesAsRead = async (ids = []) => {
  try {
    const success = await setActivitiesAsDisplayed(ids);
    if (!success) return;

    await mutate("/api/user/activities/", (activities) =>
      activities.map((activity) => ({
        ...activity,
        status: activityStatus.STATUS_DISPLAYED,
      }))
    );
  } catch (e) {
    console.log(e);
  }
};
export const dismissRequiredActionActivity = async (id) => {
  try {
    const success = await setActivityAsInteracted(id);
    if (!success) return;

    await mutate("/api/user/required-activities/", (activities) =>
      activities.map((activity) => {
        if (activity.id !== id) {
          return activity;
        }
        return {
          ...activity,
          status: activityStatus.STATUS_DISPLAYED,
        };
      })
    );
  } catch (e) {
    console.log(e);
  }
};
export const undoRequiredActionActivityDismissal = async (id) => {
  try {
    const success = await setActivityAsDisplayed(id);
    if (!success) return;

    await mutate("/api/user/required-activities/", (activities) =>
      activities.map((activity) => {
        if (activity.id !== id) {
          return activity;
        }

        return {
          ...activity,
          status: activityStatus.STATUS_DISPLAYED,
        };
      })
    );
  } catch (e) {
    console.log(e);
  }
};
