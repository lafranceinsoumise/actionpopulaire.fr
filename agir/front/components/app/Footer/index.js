import React, { Suspense, useMemo } from "react";
import { useLocation } from "react-router-dom";

import { lazy } from "@agir/front/app/utils";
import {
  getIsSessionLoaded,
  getIsConnected,
} from "@agir/front/globalContext/reducers";
import routes from "@agir/front/app/routes.config";
import { useMobileApp } from "@agir/front/app/hooks";
import { useSelector } from "@agir/front/globalContext/GlobalContext";

const Footer = lazy(() => import("./Footer"));

const ConnectedFooter = () => {
  const { pathname } = useLocation();
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const isConnected = useSelector(getIsConnected);
  const { isMobileApp } = useMobileApp();

  const route = useMemo(
    () => routes.find((route) => route.match(pathname)),
    [pathname],
  );

  if (!isSessionLoaded) {
    return null;
  }
  if (!route || route.hideFooter) {
    return null;
  }
  if (isMobileApp && !route.displayFooterOnMobileApp) {
    return null;
  }

  return (
    <Suspense fallback={<div />}>
      <Footer
        isSignedIn={isConnected}
        isMobileApp={isMobileApp}
        hasBanner={!route.hideFooterBanner && !isConnected}
      />
    </Suspense>
  );
};

export default ConnectedFooter;
