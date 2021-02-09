import shortUUID from "short-uuid";
import ACTION_TYPE from "@agir/front/globalContext/actionTypes";

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

export const topBarRightLink = (state = null, action) => {
  if (action.type === ACTION_TYPE.INIT_ACTION) {
    return action.topBarRightLink || state;
  }
  if (action.type === ACTION_TYPE.SET_TOP_BAR_RIGHT_LINK_ACTION) {
    return action.topBarRightLink || null;
  }
  return state;
};

export const messages = (state = {}, action) => {
  switch (action.type) {
    case ACTION_TYPE.SET_MESSAGES_ACTION: {
      if (!Array.isArray(action.messages)) {
        return state;
      }
      const newState = { ...state };
      action.messages.forEach((message) => {
        newState[message.id] =
          typeof newState[message.id] === "undefined"
            ? message
            : newState[message.id];
      });
      return newState;
    }
    case ACTION_TYPE.SET_MESSAGE_ACTION: {
      return action.message
        ? {
            [action.message.id]: action.message,
          }
        : {};
    }
    case ACTION_TYPE.CREATED_MESSAGE_ACTION: {
      return !action.error && action.message && action.message.id
        ? { [action.message.id]: action.message, ...state }
        : state;
    }
    case ACTION_TYPE.UPDATED_MESSAGE_ACTION: {
      if (!action.error && action.message && action.message.id) {
        const newState = { ...state };
        newState[action.message.id] = action.message;
        return newState;
      }
      return state;
    }
    case ACTION_TYPE.DELETED_MESSAGE_ACTION: {
      if (!action.error && action.message && action.message.id) {
        const newState = { ...state };
        newState[action.message.id] = null;
        return newState;
      }
      return state;
    }
    case ACTION_TYPE.CREATED_COMMENT_ACTION: {
      if (
        !action.error &&
        action.message &&
        action.message.id &&
        action.comment
      ) {
        const newState = { ...state };
        const newMessage = newState[action.message.id];
        if (newMessage) {
          newState[newMessage.id] = {
            ...newMessage,
            comments: Array.isArray(newMessage.comments)
              ? [...newMessage.comments, action.comment]
              : [...newMessage.recentComments, action.comment],
          };
          if (typeof newState[newMessage.id].commentCount === "number") {
            newState[newMessage.id].commentCount += 1;
          }
        }
        return newState;
      }
      return state;
    }
    case ACTION_TYPE.DELETED_COMMENT_ACTION: {
      if (
        !action.error &&
        action.message &&
        action.message.id &&
        action.comment
      ) {
        const newState = { ...state };
        const newMessage = newState[action.message.id];
        if (newMessage) {
          newState[newMessage.id] = {
            ...newMessage,
            comments: Array.isArray(newMessage.comments)
              ? newMessage.comments.filter((c) => c.id !== action.comment.id)
              : [],
          };
          if (typeof newState[newMessage.id].commentCount === "number") {
            newState[newMessage.id].commentCount -= 1;
          }
        }
        return newState;
      }
      return state;
    }
    default:
      return state;
  }
};

export const isLoadingMessages = (state = false, action) => {
  switch (action.type) {
    case ACTION_TYPE.LOADING_MESSAGES_ACTION:
    case ACTION_TYPE.REFRESHING_MESSAGES_ACTION:
      return true;
    case ACTION_TYPE.SET_MESSAGES_ACTION:
    case ACTION_TYPE.SET_MESSAGE_ACTION:
    case ACTION_TYPE.REFRESHED_MESSAGES_ACTION:
      return false;
    default:
      return state;
  }
};
export const isUpdatingMessages = (state = false, action) => {
  switch (action.type) {
    case ACTION_TYPE.CREATING_MESSAGE_ACTION:
    case ACTION_TYPE.UPDATING_MESSAGE_ACTION:
    case ACTION_TYPE.DELETING_MESSAGE_ACTION:
    case ACTION_TYPE.CREATING_COMMENT_ACTION:
    case ACTION_TYPE.DELETING_COMMENT_ACTION:
      return true;
    case ACTION_TYPE.CREATED_MESSAGE_ACTION:
    case ACTION_TYPE.UPDATED_MESSAGE_ACTION:
    case ACTION_TYPE.DELETED_MESSAGE_ACTION:
    case ACTION_TYPE.CREATED_COMMENT_ACTION:
    case ACTION_TYPE.DELETED_COMMENT_ACTION:
      return false;
    default:
      return state;
  }
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

export const getTopBarRightLink = (state) => {
  if (!state.topBarRightLink) return null;
  if (state.topBarRightLink.isProtected && state.isSessionLoaded && !state.user)
    return null;
  return state.topBarRightLink;
};

export const getMessages = (state) =>
  Object.values(state.messages).filter(Boolean);
export const getMessageById = (state, id) =>
  (state.messages && state.messages[id]) || null;
export const getIsLoadingMessages = (state) => state.isLoadingMessages;
export const getIsUpdatingMessages = (state) => state.isUpdatingMessages;

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
  topBarRightLink,
  messages,
  isLoadingMessages,
  isUpdatingMessages,
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
