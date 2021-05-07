import { useEffect, useMemo } from "react";
import { useHistory } from "react-router-dom";

import { parseQueryStringParams } from "@agir/lib/utils/url";

export const useCustomBackNavigation = (callback) => {
  const history = useHistory();

  useEffect(() => {
    let unblock = undefined;
    if (history && typeof callback === "function") {
      unblock = history.block(() => {
        callback();
        return false;
      });
    }
    return unblock;
  }, [callback, history]);
};

/**
 * Custom hook to check if current page is inside a iOS or Android app webview
 * based on current or past URL querystring params [ios=[0|1], android=[0|1]]
 * @return {object} the result object
 * @property {boolean} isIOS - the page is inside an iOS app webview
 * @property {boolean} isAndroid - the page is inside an Android app webview
 * @property {boolean} isMobileApp - the page is inside an app webview
 */
export const useMobileApp = () => {
  const state = useMemo(() => {
    const params = parseQueryStringParams();
    if (
      typeof window !== "undefined" &&
      window.localStorage &&
      (params.ios || params.android)
    ) {
      params.ios && window.localStorage.setItem("AP_isIOS", params.ios);
      params.android &&
        window.localStorage.setItem("AP_isAndroid", params.android);
    }
    const isIOS = window.localStorage.getItem("AP_isIOS") === "1";
    const isAndroid = window.localStorage.getItem("AP_isAndroid") === "2";

    return {
      isIOS,
      isAndroid,
      isMobileApp: isIOS || isAndroid,
    };
  }, []);

  return state;
};
