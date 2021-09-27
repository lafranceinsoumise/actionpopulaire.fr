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
  setPageTitle,
} from "@agir/front/globalContext/actions";

import Layout from "@agir/front/dashboardComponents/Layout";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";

import ErrorBoundary from "./ErrorBoundary";
import logger from "@agir/lib/utils/logger";
import useTracking from "./useTracking";

const log = logger(__filename);

const StyledPage = styled.div`
  isolation: isolate;
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

  useMemo(() => {
    if (!routeConfig.isPartial) {
      dispatch(setBackLink(null));
      dispatch(setTopBarRightLink(null));
      dispatch(setAdminLink(null));
      dispatch(setPageTitle(routeConfig?.label || null));
    }
    //eslint-disable-next-line
  }, [pathname, routeConfig]);

  useMemo(() => {
    isSessionLoaded &&
      routeConfig.backLink &&
      dispatch(setBackLink(routeConfig.backLink));
    isSessionLoaded &&
      routeConfig.topBarRightLink &&
      dispatch(setTopBarRightLink(routeConfig.topBarRightLink));
    //eslint-disable-next-line
  }, [pathname, isSessionLoaded, dispatch, routeConfig]);

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
    if (!routeConfig.keepScroll) {
      typeof window !== "undefined" &&
        !!window.scrollTo &&
        window.scrollTo(0, 0);
    }
  }, [routeConfig]);

  if (routeConfig.isPartial) {
    return (
      <ErrorBoundary>
        <Suspense fallback={<div />}>
          <Component route={routeConfig} {...routeParams} {...rest} />
        </Suspense>
      </ErrorBoundary>
    );
  }

  if (!routeConfig.hasLayout) {
    return (
      <ErrorBoundary>
        <StyledPage $hasTopBar={!routeConfig.hideTopBar}>
          <Suspense fallback={<div />}>
            <Component route={routeConfig} {...routeParams} {...rest} />
            {!routeConfig.hideFeedbackButton && (
              <FeedbackButton style={{ bottom: "1rem" }} />
            )}
          </Suspense>
        </StyledPage>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <StyledPage $hasTopBar={!routeConfig.hideTopBar}>
        <Layout active={routeConfig.id}>
          <Suspense fallback={<div />}>
            <Component route={routeConfig} {...routeParams} {...rest} />
            {!routeConfig.hideFeedbackButton && <FeedbackButton />}
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
