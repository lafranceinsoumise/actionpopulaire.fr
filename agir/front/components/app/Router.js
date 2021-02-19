import PropTypes from "prop-types";
import React, { Suspense, useEffect, useMemo } from "react";
import {
  BrowserRouter,
  Route,
  Switch,
  useHistory,
  useLocation,
  useParams,
} from "react-router-dom";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";
import {
  setBackLink,
  setTopBarRightLink,
} from "@agir/front/globalContext/actions";

import Layout from "@agir/front/dashboardComponents/Layout";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import ErrorBoundary from "./ErrorBoundary";
import routes, { BASE_PATH } from "./routes.config";
import logger from "@agir/lib/utils/logger";
import useTracking from "./useTracking";
import NotFoundPage from "@agir/front/offline/NotFoundPage";
import ConnectivityWarning from "@agir/front/app/ConnectivityWarning";

const log = logger(__filename);

const Page = (props) => {
  const history = useHistory();
  const { Component, routeConfig, ...rest } = props;
  const routeParams = useParams();
  const dispatch = useDispatch();
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const { pathname } = useLocation();

  useTracking();

  useEffect(() => {
    isSessionLoaded &&
      routeConfig.backLink &&
      dispatch(setBackLink(routeConfig.backLink));
  }, [pathname, isSessionLoaded, dispatch, routeConfig.backLink]);

  useEffect(() => {
    let unlisten = history.listen((location, action) => {
      log.debug(
        `Navigate ${action} ${location.pathname}${location.search}${location.hash}`,
        JSON.stringify(history, null, 2)
      );
    });

    return () => unlisten();
  }, [history]);

  useMemo(() => {
    typeof window !== "undefined" && window.scrollTo && window.scrollTo(0, 0);
  }, []);

  useMemo(() => {
    dispatch(setBackLink(null));
    dispatch(setTopBarRightLink(null));
    //eslint-disable-next-line
  }, [pathname]);

  if (!routeConfig.hasLayout) {
    return (
      <>
        <ConnectivityWarning />
        <ErrorBoundary>
          <Suspense fallback={<div />}>
            <Component
              {...(routeConfig.routeProps || {})}
              {...routeParams}
              {...rest}
              data={[]}
            />
            {routeConfig.hideFeedbackButton ? null : (
              <FeedbackButton style={{ bottom: "1rem" }} />
            )}
          </Suspense>
        </ErrorBoundary>
      </>
    );
  }

  return (
    <>
      <ConnectivityWarning />
      <Layout {...(routeConfig.layoutProps || {})} active={routeConfig.id}>
        <ErrorBoundary>
          <Suspense fallback={<div />}>
            <Component
              {...(routeConfig.routeProps || {})}
              {...routeParams}
              {...rest}
              data={[]}
            />
            {routeConfig.hideFeedbackButton ? null : <FeedbackButton />}
          </Suspense>
        </ErrorBoundary>
      </Layout>
    </>
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
        <NotFoundPage />
      </Route>
    </Switch>
    {children}
  </BrowserRouter>
);
Router.propTypes = {
  children: PropTypes.node,
};
export default Router;
