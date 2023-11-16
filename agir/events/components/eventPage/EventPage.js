import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { Suspense, useEffect, useMemo } from "react";
import useSWR from "swr";

import { lazy } from "@agir/front/app/utils";

import * as api from "@agir/events/common/api";
import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import {
  setAdminLink,
  setTopBarRightLink,
} from "@agir/front/globalContext/actions";
import {
  getIsConnected,
  getIsSessionLoaded,
} from "@agir/front/globalContext/reducers";
import { useIsOffline } from "@agir/front/offline/hooks";
import { routeConfig } from "@agir/front/app/routes.config";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import EventSettings from "@agir/events/EventSettings/EventSettings";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";
import OpenGraphTags from "@agir/front/app/OpenGraphTags";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import {
  ResponsiveLayout,
  useResponsiveMemo,
} from "@agir/front/genericComponents/grid";
import Skeleton from "@agir/front/genericComponents/Skeleton";

const DesktopLayout = lazy(() => import("./DesktopEventPage"));
const MobileLayout = lazy(() => import("./MobileEventPage"));

const DesktopSkeleton = () => (
  <Container style={{ margin: "4rem auto", padding: "0 4rem" }}>
    <Row gutter={32}>
      <Column grow>
        <Skeleton />
      </Column>
      <Column width="380px">
        <Skeleton />
      </Column>
    </Row>
  </Container>
);

const MobileSkeleton = () => (
  <main style={{ margin: "2rem auto", padding: "0 1rem" }}>
    <Skeleton />
  </main>
);

export const ConnectedEventPage = (props) => {
  const { eventPk } = props;

  const dispatch = useDispatch();
  const isOffline = useIsOffline();
  const isConnected = useSelector(getIsConnected);
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  const { data: eventData, error } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk }),
  );

  const EventPage = useResponsiveMemo(MobileLayout, DesktopLayout);

  useEffect(() => {
    if (
      eventData &&
      eventData.isOrganizer &&
      eventData.routes &&
      eventData.routes.manage
    ) {
      dispatch(
        setTopBarRightLink({
          to: routeConfig.eventSettings.getLink({ eventPk: eventData.id }),
          label: "Gestion de l'événement",
        }),
      );
    }
    if (eventData && eventData.routes && eventData.routes.admin) {
      dispatch(
        setAdminLink({
          href: eventData.routes.admin,
          label: "Administration",
        }),
      );
    }
  }, [eventData, dispatch]);

  useEffect(() => {
    EventPage && EventPage.preload && EventPage.preload();
  }, [EventPage]);

  const event = useMemo(() => {
    if (!eventData) {
      return eventData;
    }
    const start =
      typeof eventData.startTime === "string"
        ? DateTime.fromISO(eventData.startTime).setLocale("fr")
        : typeof eventData.startTime === "number"
          ? DateTime.fromMillis(eventData.startTime).setLocale("fr")
          : null;
    const end =
      typeof eventData.endTime === "string"
        ? DateTime.fromISO(eventData.endTime).setLocale("fr")
        : typeof eventData.endTime === "number"
          ? DateTime.fromMillis(eventData.endTime).setLocale("fr")
          : null;
    const schedule = Interval.fromDateTimes(start, end);
    const isPast = end < DateTime.local();

    const backLink = {
      route: "eventDetails",
      routeParams: { eventPk: eventData.id },
    };

    return {
      ...eventData,
      startTime: start,
      endTime: end,
      isPast,
      schedule,
      backLink,
    };
  }, [eventData]);

  if (
    error?.message === "NetworkError" ||
    [403, 404].includes(error?.response?.status) ||
    (isOffline && !eventData)
  )
    return (
      <NotFoundPage
        hasTopBar={false}
        title="Événement"
        subtitle="Cet événement"
        reloadOnReconnection={false}
      />
    );

  return (
    <>
      {eventData && (
        <OpenGraphTags
          type="article"
          title={eventData.name}
          description={eventData.textDescription}
          image={eventData.metaImage}
        />
      )}
      <PageFadeIn
        ready={isSessionLoaded && event}
        wait={
          <ResponsiveLayout
            DesktopLayout={DesktopSkeleton}
            MobileLayout={MobileSkeleton}
          />
        }
      >
        <Suspense fallback={null}>
          {event && <EventPage {...event} logged={isConnected} />}
        </Suspense>
        {event && (
          <EventSettings
            event={eventData}
            basePath={routeConfig.eventDetails.getLink({ eventPk })}
          />
        )}
      </PageFadeIn>
    </>
  );
};

ConnectedEventPage.propTypes = {
  eventPk: PropTypes.string,
};

export default ConnectedEventPage;
