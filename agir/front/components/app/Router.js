import PropTypes from "prop-types";
import React, { useEffect } from "react";
import {
  BrowserRouter,
  Redirect,
  Route,
  Switch,
  useLocation,
} from "react-router-dom";

import routes, { BASE_PATH, routeConfig } from "./routes.config";
import Page from "./Page";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage.js";

import { useAuthentication } from "@agir/front/authentication/hooks";

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
  useEffect(() => {
    const loader = document.getElementById("app_loader");
    if (!loader) {
      return;
    }
    loader.style.opacity = "0";
    loader.style.zIndex = -1;
    loader.addEventListener("transitionend", () => {
      const loader = document.getElementById("app_loader");
      loader && loader.remove();
    });
  }, []);

  return (
    <BrowserRouter basename={BASE_PATH}>
      <Switch>
        {routes.map((route) => (
          <Route key={route.id} path={route.path} exact={!!route.exact}>
            <ProtectedComponent
              Component={route.Component}
              AnonymousComponent={route.AnonymousComponent}
              route={route}
            />
          </Route>
        ))}
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
