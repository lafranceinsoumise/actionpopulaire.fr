import PropTypes from "prop-types";
import React, { Suspense, useEffect, useMemo } from "react";
import { useHistory, useLocation, useParams } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import {
  setAdminLink,
  setBackLink,
  setPageTitle,
  setTopBarRightLink,
} from "@agir/front/globalContext/actions";
import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";

import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import Layout from "@agir/front/app/Layout";

import logger from "@agir/lib/utils/logger";
import ErrorBoundary from "./ErrorBoundary";
import useTracking from "./useTracking";
import Redirect from "./Redirect";

const log = logger(__filename);

const StyledPage = styled.div`
  isolation: isolate;
  padding-top: ${({ $hasTopBar }) => ($hasTopBar ? "72px" : "0")};

  @media (max-width: ${style.collapse}px) {
    padding-top: ${({ $hasTopBar }) => ($hasTopBar ? "56px" : "0")};
  }
`;

const Page = (props) => {
  const { Component, routeConfig, hasTopBar, ...rest } = props;

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

  if (typeof routeConfig.redirectTo === "function") {
    const redirectProps = routeConfig.redirectTo(pathname, routeParams);
    return typeof redirectProps === "string" ? (
      <Redirect route={redirectProps} />
    ) : (
      <Redirect {...redirectProps} />
    );
  }

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
        <StyledPage $hasTopBar={hasTopBar}>
          <Suspense fallback={<div style={{ minHeight: "100vh" }} />}>
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
      <StyledPage $hasTopBar={hasTopBar}>
        <Layout {...(routeConfig?.layoutProps || {})} active={routeConfig.id}>
          <Suspense fallback={<div style={{ minHeight: "100vh" }} />}>
            <Component route={routeConfig} {...routeParams} {...rest} />
            {!routeConfig.hideFeedbackButton && <FeedbackButton />}
          </Suspense>
        </Layout>
      </StyledPage>
    </ErrorBoundary>
  );
};
Page.propTypes = {
  Component: PropTypes.elementType,
  routeConfig: PropTypes.object.isRequired,
  hasTopBar: PropTypes.bool,
};

export default Page;
