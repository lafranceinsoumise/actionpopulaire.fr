import PropTypes from "prop-types";
import React, { Suspense, useEffect, useMemo } from "react";
import { useHistory, useLocation, useParams } from "react-router-dom";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";
import {
  setBackLink,
  setTopBarRightLink,
  setAdminLink,
} from "@agir/front/globalContext/actions";

import Layout from "@agir/front/dashboardComponents/Layout";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import ErrorBoundary from "./ErrorBoundary";
import logger from "@agir/lib/utils/logger";
import useTracking from "./useTracking";

const log = logger(__filename);

const Page = (props) => {
  const { Component, routeConfig, ...rest } = props;

  const dispatch = useDispatch();
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const history = useHistory();
  const routeParams = useParams();
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
    dispatch(setAdminLink(null));
    //eslint-disable-next-line
  }, [pathname]);

  if (!routeConfig.hasLayout) {
    return (
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
    );
  }

  return (
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
  );
};
Page.propTypes = {
  Component: PropTypes.elementType.isRequired,
  routeConfig: PropTypes.object.isRequired,
};

export default Page;
