import PropTypes from "prop-types";
import React, { useEffect } from "react";
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

import {
  useAppLoader,
  useMobileApp,
  useDownloadBanner,
} from "@agir/front/app/hooks";

import OpenGraphTags from "@agir/front/app/OpenGraphTags";
import TopBar from "@agir/front/app/Navigation/TopBar";
import Footer from "@agir/front/app/Footer";
import ConnectivityWarning from "@agir/front/app/ConnectivityWarning";

import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

export const ProtectedComponent = (props) => {
  const { route, ...rest } = props;
  const { Component, AnonymousComponent = null } = route;

  useEffect(() => {
    const PreloadedComponent = AnonymousComponent || Component;
    if (typeof PreloadedComponent?.preload === "function") {
      log.debug("Preloading", PreloadedComponent);
      PreloadedComponent.preload();
    }
  }, [AnonymousComponent, Component]);

  const location = useLocation();
  const isAuthorized = useAuthentication(route);

  useAppLoader(isAuthorized !== null);

  if (isAuthorized === null) {
    return null;
  }

  if (isAuthorized === true) {
    return <Page Component={Component} routeConfig={route} {...rest} />;
  }

  if (AnonymousComponent) {
    const routeConfig = route.anonymousConfig
      ? {
          ...route,
          ...route.anonymousConfig,
        }
      : route;
    return (
      <Page
        Component={AnonymousComponent}
        routeConfig={routeConfig}
        {...rest}
      />
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
              <OpenGraphTags
                title={route.label}
                description={route.description}
              />
              {hasTopBar && <TopBar hasLayout={!!route.hasLayout} />}
              {hasTopBar && isBannerDownload && <Spacer size="80px" />}
              {!route.hideConnectivityWarning && (
                <ConnectivityWarning hasTopBar={hasTopBar} />
              )}
              <ProtectedComponent route={route} hasTopBar={hasTopBar} />
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
