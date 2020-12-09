import ACTION_TYPE from "./actionTypes";

import { dismissActivity } from "@agir/activity/common/helpers";

export const init = () => {
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

export const setIs2022 = () => ({
  type: ACTION_TYPE.SET_IS_2022_ACTION,
});

export const setActivityAsRead = (id) => ({
  type: ACTION_TYPE.SET_ACTIVITY_AS_READ_ACTION,
  id,
});

export const setAllActivitiesAsRead = () => ({
  type: ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION,
});

export const dismissRequiredActionActivity = (id) => async (dispatch) => {
  try {
    const success = await dismissActivity(id);
    success &&
      dispatch({
        type: ACTION_TYPE.DISMISS_REQUIRED_ACTION_ACTIVITY_ACTION,
        id,
      });
  } catch (e) {
    console.log(e);
  }
};
const createDispatch = (dispatchFunction) => (action) => {
  if (typeof action === "function") {
    return action(dispatchFunction);
  }
  return dispatchFunction(action);
};

export default createDispatch;
