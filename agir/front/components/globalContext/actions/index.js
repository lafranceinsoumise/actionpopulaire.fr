import ACTION_TYPE from "@agir/front/globalContext/actionTypes";

export const initFromScriptTag = (hasRouter = false) => {
  const globalContextScript = document.getElementById("globalContext");
  let globalContextData = { hasRouter };
  if (globalContextScript) {
    globalContextData = {
      ...globalContextData,
      ...JSON.parse(globalContextScript.textContent),
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

// IS BANNER DOWNLOAD
export const setBannerDownload = () => ({
  type: ACTION_TYPE.ADD_BANNER_DOWNLOAD,
});
export const clearBannerDownload = () => ({
  type: ACTION_TYPE.CLEAR_BANNER_DOWNLOAD,
});

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

// ADMIN LINK
export const setAdminLink = (adminLink) => ({
  type: ACTION_TYPE.SET_ADMIN_LINK_ACTION,
  adminLink,
});

const createDispatch = (dispatchFunction) => (action) => {
  if (typeof action === "function") {
    return action(dispatchFunction);
  }
  return dispatchFunction(action);
};

export default createDispatch;
