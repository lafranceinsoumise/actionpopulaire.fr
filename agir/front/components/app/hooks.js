import querystring from "query-string";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import { createGlobalState } from "react-use";

import { getRouteByPathname, routeConfig } from "@agir/front/app/routes.config";
import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getHasRouter, getRoutes } from "@agir/front/globalContext/reducers";
import { useLocalStorage } from "@agir/lib/utils/hooks";
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

/**
 * Custom React hook to hide the application loader
 * @param  {Boolean} [isReady=true]               whether the loader can be hidden or not
 */
export const useAppLoader = (isReady = true) => {
  const [loader, setLoader] = useState(
    isReady ? document.getElementById("app_loader") : null,
  );

  useEffect(() => {
    isReady !== null && setLoader(document.getElementById("app_loader"));
  }, [isReady]);

  useEffect(() => {
    if (!loader) {
      return;
    }

    loader.addEventListener("transitionend", () => {
      const loader = document.getElementById("app_loader");
      loader && loader.remove();
    });
    loader.style.opacity = "0";
    loader.style.zIndex = -1;

    setLoader(null);
  }, [loader]);
};

export const useRoute = (route, routeParams) => {
  const routes = useSelector(getRoutes);
  const hasRouter = useSelector(getHasRouter);

  if (!route) {
    return {
      route: null,
      isInternal: false,
    };
  }

  if (routes && routes[route]) {
    return {
      url: routes[route],
      isInternal: !!hasRouter && !!getRouteByPathname(routes[route]),
    };
  }

  if (routeConfig[route]) {
    return {
      url: routeParams
        ? routeConfig[route].getLink(routeParams)
        : routeConfig[route].getLink(),
      isInternal: !!hasRouter,
    };
  }

  return {
    url: route,
    isInternal: false,
  };
};

export const useLocationState = () => {
  const { search, pathname } = useLocation();
  const history = useHistory();

  const params = useMemo(
    () => querystring.parse(search, { arrayFormat: "comma" }),
    [search],
  );

  const setParams = useCallback(
    (key, value) => {
      history.replace({
        pathname,
        search: querystring.stringify(
          {
            ...params,
            [key]: value,
          },
          { arrayFormat: "comma" },
        ),
      });
    },
    [pathname, history, params],
  );

  const clearParams = useCallback(() => {
    history.replace({
      pathname,
      search: querystring.stringify({}, { arrayFormat: "comma" }),
    });
  }, [pathname, history]);

  return [params, setParams, !!search ? clearParams : undefined];
};
