import { useCallback, useEffect, useMemo } from "react";
import { useHistory } from "react-router-dom";
import { createGlobalState } from "react-use";

import { parseQueryStringParams } from "@agir/lib/utils/url";
import { useLocalStorage } from "@agir/lib/utils/hooks";
import { useIsDesktop } from "@agir/front/genericComponents/grid.js";

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
  const [isAndroid, setIsAndroid] = useLocalStorage("AP_isAndroid", "0");
  const [isIOS, setIsIOS] = useLocalStorage("AP_isIOS", "0");

  const state = useMemo(() => {
    const params = parseQueryStringParams();

    if (params.ios || params.android) {
      params.ios && setIsIOS(params.ios);
      params.android && setIsAndroid(params.android);
    }

    const ios = isIOS === "1" || params.ios === "1";
    const android = isAndroid === "1" || params.android === "1";

    return {
      isIOS: ios,
      isAndroid: android,
      isMobileApp: ios || android,
    };
    // eslint-disable-next-line
  }, []);

  return state;
};

const useHasDownloadBanner = createGlobalState(undefined);
export const useDownloadBanner = () => {
  const [bannerCount, setBannerCount] = useLocalStorage("BANNER_count", 0);
  const [visitCount] = useLocalStorage("AP_vcount", 0);

  const isDesktop = useIsDesktop();
  const { isMobileApp } = useMobileApp();

  const [hasBanner, setHasBanner] = useHasDownloadBanner();

  useEffect(() => {
    if (
      hasBanner !== false &&
      !isMobileApp &&
      !isDesktop &&
      bannerCount <= visitCount
    ) {
      setHasBanner(true);
    }
  }, [
    hasBanner,
    isMobileApp,
    isDesktop,
    bannerCount,
    visitCount,
    setHasBanner,
  ]);

  const hide = useCallback(() => {
    setHasBanner(false);
    setBannerCount(visitCount + 25);
  }, [setBannerCount, visitCount, setHasBanner]);

  return [!!hasBanner, hide];
};
