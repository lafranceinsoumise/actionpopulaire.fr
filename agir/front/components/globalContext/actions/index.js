import ACTION_TYPE from "@agir/front/globalContext/actionTypes";
import nonReactRoutes from "@agir/front/globalContext/nonReactRoutes.config";

export const init = (hasRouter = false) => {
  let globalContextData = {
    hasRouter,
    routes: nonReactRoutes,
  };

  return {
    type: ACTION_TYPE.INIT_ACTION,
    ...globalContextData,
  };
};

export const setSessionContext = (data) => ({
  type: ACTION_TYPE.SET_SESSION_CONTEXT_ACTION,
  ...data,
});

export const setisPoliticalSupport = () => ({
  type: ACTION_TYPE.SET_IS_POLITICAL_SUPPORT_ACTION,
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

// PAGE TITLE
export const setPageTitle = (title) => ({
  type: ACTION_TYPE.SET_PAGE_TITLE,
  title,
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
