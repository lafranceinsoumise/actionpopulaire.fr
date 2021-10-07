import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import {
  BrowserRouter,
  Redirect,
  Route,
  Switch,
  useLocation,
} from "react-router-dom";
import ScrollMemory from "react-router-scroll-memory";

import routes, { BASE_PATH, routeConfig } from "./routes.config";
import Page from "./Page";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";

import { useAuthentication } from "@agir/front/authentication/hooks";

import Spacer from "@agir/front/genericComponents/Spacer";

import { useMobileApp, useDownloadBanner } from "@agir/front/app/hooks";

import TopBar from "@agir/front/allPages/TopBar/TopBar";
import Footer from "@agir/front/app/Footer";
import ConnectivityWarning from "@agir/front/app/ConnectivityWarning";

import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

export const ProtectedComponent = ({
  Component,
  AnonymousComponent = null,
  route,
  ...rest
}) => {
  const location = useLocation();
  const isAuthorized = useAuthentication(route);

  useEffect(() => {
    const PreloadedComponent = AnonymousComponent || Component;
    if (typeof PreloadedComponent.preload === "function") {
      log.debug("Preloading", PreloadedComponent);
      PreloadedComponent.preload();
    }
  }, [AnonymousComponent, Component]);

  const [loader, setLoader] = useState();

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

  useEffect(() => {
    isAuthorized !== null && setLoader(document.getElementById("app_loader"));
  }, [isAuthorized]);

  if (isAuthorized === null) {
    return null;
  }

  if (isAuthorized === true) {
    return <Page Component={Component} routeConfig={route} {...rest} />;
  }

  if (AnonymousComponent) {
    return (
      <Page Component={AnonymousComponent} routeConfig={route} {...rest} />
    );
  }

  return (
    <Redirect
      to={{
        pathname: routeConfig.login.getLink(),
        state: { next: location.pathname },
      }}
    />
  );
};
ProtectedComponent.propTypes = {
  Component: PropTypes.elementType.isRequired,
  AnonymousComponent: PropTypes.elementType,
  route: PropTypes.object.isRequired,
};

const Router = ({ children }) => {
  const { isMobileApp } = useMobileApp();
  const [isBannerDownload] = useDownloadBanner();

  return (
    <BrowserRouter basename={BASE_PATH}>
      <ScrollMemory />
      <Switch>
        {routes.map((route) => {
          const hasTopBar =
            !route.hideTopBar && (!route.appOnlyTopBar || isMobileApp);
          return (
            <Route key={route.id} path={route.path} exact={!!route.exact}>
              {hasTopBar && <TopBar />}
              {hasTopBar && isBannerDownload && <Spacer size="80px" />}
              {!route.hideConnectivityWarning && (
                <ConnectivityWarning hasTopBar={hasTopBar} />
              )}
              <ProtectedComponent
                Component={route.Component}
                AnonymousComponent={route.AnonymousComponent}
                route={route}
                hasTopBar={hasTopBar}
              />
              {!route.hideFooter && (
                <Footer
                  hideBanner={route.hideFooterBanner}
                  displayOnMobileApp={route.displayFooterOnMobileApp}
                />
              )}
            </Route>
          );
        })}
        <Route key="not-found">
          <NotFoundPage />
        </Route>
      </Switch>
      {children}
    </BrowserRouter>
  );
};

Router.propTypes = {
  children: PropTypes.node,
};
export default Router;
