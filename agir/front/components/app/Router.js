import PropTypes from "prop-types";
import React, { Suspense } from "react";
import { BrowserRouter, Switch, Route } from "react-router-dom";

import ErrorBoundary from "./ErrorBoundary";
import Link from "./Link";
import Button from "@agir/front/genericComponents/Button";

import routes, { BASE_PATH } from "./routes.config";

const NotFound = () => <div>404 NOT FOUND !</div>;

const Router = ({ children }) => (
  <BrowserRouter basename={BASE_PATH}>
    <div>
      <nav>
        <ul>
          {routes.map((route) => (
            <li key={route.id}>
              <Link to={route}>{route.label}</Link>
            </li>
          ))}
          <li key="etc">
            <Link href="https://actionpopulaire.fr">Une page externe</Link>
            <Button
              href="https://actionpopulaire.fr"
              as="Link"
              color="secondary"
            >
              Bouton
            </Button>
            <Button to={routes[0]} as="Link" color="primary">
              Une route
            </Button>
            <Button route="dashboard" as="Link" color="primary">
              Une route backend
            </Button>
          </li>
        </ul>
      </nav>
      <Suspense fallback={<div />}>
        <Switch>
          {routes.map((route) => (
            <Route key={route.id} path={route.pathname} exact={!!route.exact}>
              {
                <ErrorBoundary>
                  <route.Component data={[]} routeConfig={route} />
                </ErrorBoundary>
              }
            </Route>
          ))}
          <Route key="not-found">
            <NotFound />
          </Route>
        </Switch>
      </Suspense>
      {children}
    </div>
  </BrowserRouter>
);
Router.propTypes = {
  children: PropTypes.node,
};
export default Router;
