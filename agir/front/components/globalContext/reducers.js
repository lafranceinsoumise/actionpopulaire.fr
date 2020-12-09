import ACTION_TYPE from "./actionTypes";
import {
  activityStatus,
  getUnreadCount,
  parseActivities,
} from "@agir/activity/common/helpers";

// Reducers
const domain = "https://actionpopulaire.fr";

const hasFeedbackButton = (state = false, action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return !!action.hasFeedbackButton;
  }
  return state;
};

const is2022 = (state = false, action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return !!action.user && action.user.is2022;
  }
  if (action.type === ACTION_TYPE.SET_IS_2022_ACTION) {
    return true;
  }
  return state;
};

const announcements = (state = [], action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return action.announcements || state;
  }
  return state;
};

const activities = (state = [], action) => {
  switch (action.type) {
    case ACTION_TYPE.INIT_ACTION: {
      if (!Array.isArray(action.activities)) {
        return state;
      }
      const { unrequired } = parseActivities(action.activities);
      return unrequired;
    }
    case ACTION_TYPE.MARK_ACTIVITY_AS_READ_ACTION: {
      if (!action.id) {
        return state;
      }
      return state.map((activity) => {
        if (activity.id !== action.id) {
          return activity;
        }
        return {
          ...activity,
          status: activityStatus.STATUS_DISPLAYED,
        };
      });
    }
    case ACTION_TYPE.MARK_ALL_ACTIVITIES_AS_READ_ACTION: {
      return state.map((activity) => ({
        ...activity,
        status: activityStatus.STATUS_DISPLAYED,
      }));
    }
    default:
      return state;
  }
};

const requiredActionActivities = (state = [], action) => {
  if (
    action.type === ACTION_TYPE.INIT_ACTION &&
    Array.isArray(action.activities)
  ) {
    const { required } = parseActivities(action.activities);

    return required;
  }
  if (
    action.type === ACTION_TYPE.DISMISS_REQUIRED_ACTION_ACTIVITY_ACTION &&
    action.id
  ) {
    return state.filter((activity) => activity.id !== action.id);
  }
  return state;
};

const user = (state = null, action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return action.user || null;
  }
  return state;
};

const csrfToken = (state = null, action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return action.csrfToken || null;
  }
  return state;
};

const routes = (state = {}, action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return action.routes || null;
  }
  return state;
};

// Selectors
export const getDomain = (state) => state.domain;

export const getHasFeedbackButton = (state) => state.hasFeedbackButton;

export const getIs2022 = (state) => state.is2022;

export const getAnnouncements = (state) => state.announcements;

export const getActivities = (state) => state.activities;
export const getUnreadActivitiesCount = (state) =>
  getUnreadCount(state.activities);

export const getRequiredActionActivities = (state) =>
  state.requiredActionActivities;
export const getRequiredActionActivityCount = (state) =>
  state.requiredActionActivities.length;

export const getUser = (state) => state.user;
export const getIsConnected = (state) => !!state.user;

export const getCsrfToken = (state) => state.csrfToken;

export const getRoutes = (state) => state.routes;
export const getRouteById = (state, id) => state.routes[id] || null;

// Root reducer
const reducers = {
  hasFeedbackButton,
  is2022,
  announcements,
  activities,
  requiredActionActivities,
  user,
  domain,
  csrfToken,
  routes,
};
const rootReducer = (state, action) => {
  let newState = state;
  Object.keys(reducers).forEach((key) => {
    const currentValue = newState[key];
    const reducer = reducers[key];
    const nextValue =
      typeof reducer === "function" ? reducer(currentValue, action) : reducer;
    if (nextValue !== currentValue) {
      newState = {
        ...newState,
        [key]: nextValue,
      };
    }
  });
  return newState;
};

export default rootReducer;
