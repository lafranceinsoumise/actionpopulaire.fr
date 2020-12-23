import PropTypes from "prop-types";
import React, { Suspense } from "react";
import { BrowserRouter, Switch, Route, useParams } from "react-router-dom";

import ErrorBoundary from "./ErrorBoundary";
import Link from "./Link";
import Button from "@agir/front/genericComponents/Button";

import routes, { BASE_PATH } from "./routes.config";

const NotFound = () => <div>404 NOT FOUND !</div>;

const Page = (props) => {
  const { Component, ...rest } = props;
  const routeParams = useParams();
  return (
    <ErrorBoundary>
      <Component {...routeParams} {...rest} />
    </ErrorBoundary>
  );
};
Page.propTypes = {
  Component: PropTypes.elementType,
};

const Router = ({ children }) => (
  <BrowserRouter basename={BASE_PATH}>
    <div>
      <nav>
        <ul>
          {routes.map((route) => (
            <li key={route.id}>
              <Link
                to={route.getLink({
                  eventPk: "54e7f6e2-f816-4630-9277-1317ff52b1db/",
                })}
              >
                {route.label}
              </Link>
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
              <Page Component={route.Component} data={[]} />
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
