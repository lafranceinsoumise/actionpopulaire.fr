import PropTypes from "prop-types";
import React, { Suspense, useEffect, useMemo } from "react";
import { useHistory, useLocation, useParams } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Spacer from "@agir/front/genericComponents/Spacer";

import { useDownloadBanner } from "@agir/front/app/hooks.js";
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

import ConnectivityWarning from "@agir/front/app/ConnectivityWarning";
import Layout from "@agir/front/dashboardComponents/Layout";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import TopBar from "@agir/front/allPages/TopBar";

import ErrorBoundary from "./ErrorBoundary";
import logger from "@agir/lib/utils/logger";
import useTracking from "./useTracking";

import { routeConfig as routesConfig } from "@agir/front/app/routes.config";

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
  const [isBannerDownload] = useDownloadBanner();
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
    if (
      [
        routesConfig.events.path,
        routesConfig.activities.path,
        routesConfig.groups.path,
      ].includes(pathname)
    ) {
      return;
    }
    typeof window !== "undefined" && window.scrollTo && window.scrollTo(0, 0);
  }, [pathname]);

  if (routeConfig.isPartial) {
    return (
      <ErrorBoundary>
        <Suspense fallback={<div />}>
          <Component
            {...(routeConfig.routeProps || {})}
            {...routeParams}
            {...rest}
          />
        </Suspense>
      </ErrorBoundary>
    );
  }

  if (!routeConfig.hasLayout) {
    return (
      <ErrorBoundary>
        {routeConfig.hideTopBar ? null : <TopBar path={pathname} />}

        {!routeConfig.hideTopBar && isBannerDownload && <Spacer size="80px" />}

        <StyledPage $hasTopBar={!routeConfig.hideTopBar}>
          {routeConfig.hideConnectivityWarning ? null : (
            <ConnectivityWarning hasTopBar={!routeConfig.hideTopBar} />
          )}
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
        </StyledPage>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      {routeConfig.hideTopBar ? null : <TopBar path={pathname} />}

      {!routeConfig.hideTopBar && isBannerDownload && <Spacer size="80px" />}

      {routeConfig.hideConnectivityWarning ? null : (
        <ConnectivityWarning hasTopBar={!routeConfig.hideTopBar} />
      )}
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
