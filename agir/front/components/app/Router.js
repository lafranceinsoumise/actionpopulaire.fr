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

import { useAppLoader, useMobileApp } from "@agir/front/app/hooks";
import { useAuthentication } from "@agir/front/authentication/hooks";
import routes, { BASE_PATH, routeConfig } from "./routes.config";
import useTracking from "./useTracking";

import ConnectivityWarning from "@agir/front/app/ConnectivityWarning";
import Footer from "@agir/front/app/Footer";
import TopBar from "@agir/front/app/Navigation/TopBar";
import OpenGraphTags from "@agir/front/app/OpenGraphTags";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";
import Page from "./Page";

import logger from "@agir/lib/utils/logger";
import ModalMissingNewsletter from "@agir/front/app/ModalMissingNewsletter";

const log = logger(__filename);

export const ProtectedComponent = (props) => {
  const { route, ...rest } = props;
  const { Component, AnonymousComponent = null } = route;

  const location = useLocation();
  const isAuthorized = useAuthentication(route);

  useAppLoader(isAuthorized !== null);
  useEffect(() => {
    if (isAuthorized === null) {
      return;
    }
    const PreloadedComponent = isAuthorized ? Component : AnonymousComponent;
    if (
      PreloadedComponent &&
      typeof PreloadedComponent.preload === "function"
    ) {
      log.debug("Preloading", PreloadedComponent);
      PreloadedComponent.preload();
    }
  }, [isAuthorized, AnonymousComponent, Component]);

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

const TrackingComponent = () => {
  useTracking();
  return null;
};
const Router = ({ children }) => {
  const { isMobileApp } = useMobileApp();
  return (
    <BrowserRouter basename={BASE_PATH}>
      <ModalMissingNewsletter />
      <TrackingComponent />
      <ScrollMemory />
      <TopBar />
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
              {!route.hideConnectivityWarning && (
                <ConnectivityWarning hasTopBar={hasTopBar} />
              )}
              <ProtectedComponent route={route} hasTopBar={hasTopBar} />
            </Route>
          );
        })}
        <Route key="not-found">
          <NotFoundPage />
        </Route>
      </Switch>
      {children}
      <Footer />
    </BrowserRouter>
  );
};

Router.propTypes = {
  children: PropTypes.node,
};
export default Router;
