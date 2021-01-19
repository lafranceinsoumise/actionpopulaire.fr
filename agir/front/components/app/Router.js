import PropTypes from "prop-types";
import React, { Suspense, useEffect } from "react";
import { BrowserRouter, Switch, Route, useParams } from "react-router-dom";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";
import { setBackLink } from "@agir/front/globalContext/actions";

import Layout from "@agir/front/dashboardComponents/Layout";
import ErrorBoundary from "./ErrorBoundary";

import routes, { BASE_PATH } from "./routes.config";

const NotFound = () => <div>404 NOT FOUND !</div>;

const Page = (props) => {
  const { Component, routeConfig, ...rest } = props;
  const routeParams = useParams();
  const dispatch = useDispatch();
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  useEffect(() => {
    dispatch(setBackLink(routeConfig.backLink));
    return () => {
      dispatch(setBackLink(null));
    };
  }, [isSessionLoaded, dispatch, routeConfig.backLink]);

  if (!routeConfig.hasLayout) {
    return (
      <ErrorBoundary>
        <Suspense fallback={<div />}>
          <Component {...routeParams} {...rest} data={[]} />
        </Suspense>
      </ErrorBoundary>
    );
  }

  return (
    <Layout {...(routeConfig.layoutProps || {})} active={routeConfig.id}>
      <ErrorBoundary>
        <Suspense fallback={<div />}>
          <Component {...routeParams} {...rest} data={[]} />
        </Suspense>
      </ErrorBoundary>
    </Layout>
  );
};
Page.propTypes = {
  Component: PropTypes.elementType.isRequired,
  routeConfig: PropTypes.object.isRequired,
};

const Router = ({ children }) => (
  <BrowserRouter basename={BASE_PATH}>
    <Switch>
      {routes.map((route) => (
        <Route key={route.id} path={route.pathname} exact={!!route.exact}>
          <Page Component={route.Component} routeConfig={route} />
        </Route>
      ))}
      <Route key="not-found">
        <NotFound />
      </Route>
    </Switch>
    {children}
  </BrowserRouter>
);
Router.propTypes = {
  children: PropTypes.node,
};
export default Router;
