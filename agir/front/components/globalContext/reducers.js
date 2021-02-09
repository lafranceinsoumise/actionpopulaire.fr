import shortUUID from "short-uuid";
import ACTION_TYPE from "./actionTypes";

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

// Selectors
export const getDomain = (state) => state.domain;

export const getHasFeedbackButton = (state) => state.hasFeedbackButton;

export const getIsSessionLoaded = (state) => state.isSessionLoaded;

export const getIs2022 = (state) => state.is2022;

export const getUser = (state) => state.user;
export const getIsConnected = (state) => !!state.user;

export const getCsrfToken = (state) => state.csrfToken;

export const getRoutes = (state) => state.routes;
export const getRouteById = (state, id) => state.routes[id] || null;

export const getToasts = (state) => state.toasts;

// Root reducer
const reducers = {
  hasFeedbackButton,
  isSessionLoaded,
  is2022,
  user,
  domain,
  csrfToken,
  routes,
  toasts,
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
