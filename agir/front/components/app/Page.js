import PropTypes from "prop-types";
import React, { Suspense, useEffect, useMemo } from "react";
import { useHistory, useLocation, useParams } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

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

import ConnectivityWarning from "@agir/front/app/ConnectivityWarning";
import Layout from "@agir/front/dashboardComponents/Layout";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import TopBar from "@agir/front/allPages/TopBar";

import ErrorBoundary from "./ErrorBoundary";
import logger from "@agir/lib/utils/logger";
import useTracking from "./useTracking";

const log = logger(__filename);

const StyledPage = styled.div`
  ${({ $hasTopBar }) =>
    $hasTopBar
      ? `
        padding-top: 72px;

        @media (max-width: ${style.collapse}px) {
          padding-top: 56px;
        }
      `
      : ""}
`;

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
        <StyledPage $hasTopBar={!routeConfig.hideTopBar}>
          {routeConfig.hideTopBar ? null : <TopBar />}
          <ConnectivityWarning hasTopBar={!routeConfig.hideTopBar} />
          <Suspense fallback={<div />}>
            <Component
              {...(routeConfig.routeProps || {})}
              {...routeParams}
              {...rest}
              data={[]}
            />
            {routeConfig.hideFeedbackButton ? null : (
              <FeedbackButton />
            )}
          </Suspense>
        </StyledPage>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      {routeConfig.hideTopBar ? null : <TopBar />}
      <ConnectivityWarning hasTopBar={!routeConfig.hideTopBar} />
      <StyledPage $hasTopBar={!routeConfig.hideTopBar}>
        <Layout {...(routeConfig.layoutProps || {})} active={routeConfig.id}>
          <Suspense fallback={<div />}>
            <Component
              {...(routeConfig.routeProps || {})}
              {...routeParams}
              {...rest}
              data={[]}
            />
            {routeConfig.hideFeedbackButton ? null : <FeedbackButton />}
          </Suspense>
        </Layout>
      </StyledPage>
    </ErrorBoundary>
  );
};
Page.propTypes = {
  Component: PropTypes.elementType.isRequired,
  routeConfig: PropTypes.object.isRequired,
};

export default Page;
