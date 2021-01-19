import ACTION_TYPE from "./actionTypes";

import {
  setActivityAsInteracted,
  setActivityAsDisplayed,
  setActivitiesAsDisplayed,
} from "@agir/activity/common/helpers";

export const initFromScriptTag = () => {
  const globalContextScript = document.getElementById("globalContext");
  const extraContextScript = document.getElementById("extraContext");

  let globalContextData = {};
  if (globalContextScript) {
    globalContextData = {
      ...globalContextData,
      ...JSON.parse(globalContextScript.textContent),
    };
  }
  if (extraContextScript) {
    globalContextData = {
      ...globalContextData,
      ...JSON.parse(extraContextScript.textContent),
    };
  }

  return {
    type: ACTION_TYPE.INIT_ACTION,
    ...globalContextData,
  };
};

export const setSessionContext = (data) => ({
  type: ACTION_TYPE.SET_SESSION_CONTEXT_ACTION,
  ...data,
});

export const setIs2022 = () => ({
  type: ACTION_TYPE.SET_IS_2022_ACTION,
});

// ACTIVITIES
export const setActivityAsRead = (id) => ({
  type: ACTION_TYPE.SET_ACTIVITY_AS_READ_ACTION,
  id,
});

export const setAllActivitiesAsRead = (ids = [], updateState = false) => async (
  dispatch
) => {
  try {
    const success = await setActivitiesAsDisplayed(ids);
    updateState &&
      success &&
      dispatch({
        type: ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION,
      });
  } catch (e) {
    console.log(e);
  }
};

// REQUIRED ACTION ACTIVITIES
export const dismissRequiredActionActivity = (id) => async (dispatch) => {
  try {
    const success = await setActivityAsInteracted(id);
    success &&
      dispatch({
        type: ACTION_TYPE.DISMISS_REQUIRED_ACTION_ACTIVITY_ACTION,
        id,
      });
  } catch (e) {
    console.log(e);
  }
};

export const undoRequiredActionActivityDismissal = (id) => async (dispatch) => {
  try {
    const success = await setActivityAsDisplayed(id);
    success &&
      dispatch({
        type: ACTION_TYPE.UNDO_REQUIRED_ACTION_ACTIVITY_DISMISSAL_ACTION,
        id,
      });
  } catch (e) {
    console.log(e);
  }
};

// ANNOUNCEMENTS
export const setAnnouncementsAsRead = (ids = []) => async (dispatch) => {
  try {
    const success = await setActivitiesAsDisplayed(ids);
    success &&
      dispatch({
        type: ACTION_TYPE.SET_ANNOUNCEMENTS_AS_READ_ACTION,
      });
  } catch (e) {
    console.log(e);
  }
};

// TOASTS
export const addToasts = (toasts = []) => ({
  type: ACTION_TYPE.ADD_TOASTS,
  toasts: Array.isArray(toasts) ? toasts : [toasts],
});
export const clearToast = (toastId) => ({
  type: ACTION_TYPE.CLEAR_TOAST,
  toastId,
});
export const clearAllToasts = () => ({
  type: ACTION_TYPE.CLEAR_ALL_TOASTS,
});

const createDispatch = (dispatchFunction) => (action) => {
  if (typeof action === "function") {
    return action(dispatchFunction);
  }
  return dispatchFunction(action);
};

// BACK LINK
export const setBackLink = (backLink) => ({
  type: ACTION_TYPE.SET_BACK_LINK_ACTION,
  backLink,
});

// TOP BAR RIGHT LINK
export const setTopBarRightLink = (topBarRightLink) => ({
  type: ACTION_TYPE.SET_TOP_BAR_RIGHT_LINK_ACTION,
  topBarRightLink,
});

export default createDispatch;
