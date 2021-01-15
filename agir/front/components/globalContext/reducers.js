import shortUUID from "short-uuid";
import ACTION_TYPE from "./actionTypes";

import {
  activityStatus,
  getUnreadCount,
  getUninteractedCount,
} from "@agir/activity/common/helpers";

// Reducers
export const domain = (state = "https://actionpopulaire.fr", action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return action.domain || state;
  }
  return state;
};

export const isSessionLoaded = (state = false, action) => {
  if (action.type === ACTION_TYPE.SET_SESSION_CONTEXT_ACTION) {
    return true;
  }
  return state;
};

export const hasFeedbackButton = (state = false, action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return !!action.hasFeedbackButton;
  }
  return state;
};

export const is2022 = (state = false, action) => {
  if (action.type === ACTION_TYPE.SET_SESSION_CONTEXT_ACTION) {
    return !!action.user && action.user.is2022;
  }
  if (action.type === ACTION_TYPE.SET_IS_2022_ACTION) {
    return true;
  }
  return state;
};

export const announcements = (state = [], action) => {
  if (action.type === ACTION_TYPE.SET_SESSION_CONTEXT_ACTION) {
    return action.announcements || state;
  }
  return state;
};

export const activities = (state = [], action) => {
  switch (action.type) {
    case ACTION_TYPE.SET_SESSION_CONTEXT_ACTION: {
      if (!Array.isArray(action.activities)) {
        return state;
      }
      return action.activities;
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
    case ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION: {
      return state.map((activity) => ({
        ...activity,
        status: activityStatus.STATUS_DISPLAYED,
      }));
    }
    default:
      return state;
  }
};

export const requiredActionActivities = (state = [], action) => {
  if (
    action.type === ACTION_TYPE.SET_SESSION_CONTEXT_ACTION &&
    Array.isArray(action.requiredActionActivities)
  ) {
    return action.requiredActionActivities;
  }
  if (
    action.type === ACTION_TYPE.DISMISS_REQUIRED_ACTION_ACTIVITY_ACTION &&
    action.id
  ) {
    return state.map((activity) =>
      activity.id === action.id
        ? {
            ...activity,
            status: activityStatus.STATUS_INTERACTED,
          }
        : activity
    );
  }
  if (
    action.type ===
      ACTION_TYPE.UNDO_REQUIRED_ACTION_ACTIVITY_DISMISSAL_ACTION &&
    action.id
  ) {
    return state.map((activity) =>
      activity.id === action.id
        ? {
            ...activity,
            status: activityStatus.STATUS_DISPLAYED,
          }
        : activity
    );
  }
  return state;
};

export const user = (state = null, action) => {
  if (action.type === ACTION_TYPE.SET_SESSION_CONTEXT_ACTION) {
    return action.user || state;
  }
  return state;
};

export const csrfToken = (state = null, action) => {
  if (action.type === ACTION_TYPE.SET_SESSION_CONTEXT_ACTION) {
    return action.csrfToken || state;
  }
  return state;
};

export const routes = (state = {}, action) => {
  if (
    action.type === ACTION_TYPE.INIT_ACTION ||
    action.type === ACTION_TYPE.SET_SESSION_CONTEXT_ACTION
  ) {
    // Merge state and action payload since different actions can define different route properties.
    return {
      ...state,
      ...(action.routes || {}),
    };
  }
  return state;
};

export const toasts = (state = [], action) => {
  if (
    action.type === ACTION_TYPE.SET_SESSION_CONTEXT_ACTION ||
    action.type === ACTION_TYPE.ADD_TOASTS
  ) {
    return Array.isArray(action.toasts)
      ? action.toasts.map((toast) => ({
          toastId: shortUUID.generate(),
          ...toast,
        }))
      : state;
  }
  if (action.type === ACTION_TYPE.CLEAR_TOAST) {
    return state.filter(({ toastId }) => toastId !== action.toastId);
  }
  if (action.type === ACTION_TYPE.CLEAR_ALL_TOASTS) {
    return [];
  }
  return state;
};

export const backLink = (state = null, action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return action.backLink || state;
  }
  if (action.type === ACTION_TYPE.SET_BACK_LINK_ACTION) {
    return action.backLink || null;
  }
  return state;
};

// Selectors
export const getDomain = (state) => state.domain;

export const getHasFeedbackButton = (state) => state.hasFeedbackButton;

export const getIsSessionLoaded = (state) => state.isSessionLoaded;

export const getIs2022 = (state) => state.is2022;

export const getAnnouncements = (state) => state.announcements;

export const getActivities = (state) => state.activities;
export const getUnreadActivitiesCount = (state) =>
  getUnreadCount(state.activities);

export const getRequiredActionActivities = (state) =>
  state.requiredActionActivities;
export const getRequiredActionActivityCount = (state) =>
  getUninteractedCount(state.requiredActionActivities);

export const getUser = (state) => state.user;
export const getIsConnected = (state) => !!state.user;

export const getCsrfToken = (state) => state.csrfToken;

export const getRoutes = (state) => state.routes;
export const getRouteById = (state, id) => state.routes[id] || null;

export const getToasts = (state) => state.toasts;

export const getBackLink = (state) => {
  if (!state.backLink) return null;
  if (state.backLink.isProtected && state.isSessionLoaded && !state.user)
    return null;
  return state.backLink;
};

// Root reducer
const reducers = {
  hasFeedbackButton,
  isSessionLoaded,
  is2022,
  announcements,
  activities,
  requiredActionActivities,
  user,
  domain,
  csrfToken,
  routes,
  toasts,
  backLink,
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
