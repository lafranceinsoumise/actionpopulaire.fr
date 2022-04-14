import React, { useCallback, useEffect, useState } from "react";
import { Redirect, useRouteMatch, useLocation } from "react-router-dom";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { usePush } from "@agir/notifications/push/subscriptions";
import { routeConfig } from "@agir/front/app/routes.config";
import { useMobileApp } from "@agir/front/app/hooks";

import TellMore from "./TellMore";
import ChooseCampaign from "./ChooseCampaign";
import ChooseNewsletters from "./ChooseNewsletters";
import DeviceNotificationSubscription from "./DeviceNotificationSubscription";

const TellMorePage = () => {
  const location = useLocation();

  const isTellMorePage = useRouteMatch(routeConfig.tellMore.getLink());

  const { available, isSubscribed, subscribe, ready, errorMessage } = usePush();

  const [hasCampaign, dismissCampaign, campaignIsLoading] =
    useCustomAnnouncement("chooseCampaign", false);

  const [hasNewsletters, dismissNewsletters, newslettersAreLoading] =
    useCustomAnnouncement("ChooseNewsletters", false);

  const [hasTellMore, dismissTellMore, tellMoreIsLoading] =
    useCustomAnnouncement("tellMore", false);

  const [
    hasDeviceNotificationSubscription,
    setHasDeviceNotificationSubscription,
  ] = useState(isTellMorePage);

  const dismissDeviceNotificationSubscription = useCallback(() => {
    setHasDeviceNotificationSubscription(false);
  }, []);

  const { isMobileApp } = useMobileApp();

  useEffect(() => {
    let timeout = null;
    // Avoid blocking the user on a blank page if push never becomes ready
    if (isMobileApp && hasDeviceNotificationSubscription && !ready) {
      timeout = setTimeout(() => {
        setHasDeviceNotificationSubscription(false);
      }, 1000);
    }
    return () => {
      timeout && clearTimeout(timeout);
    };
  }, [hasDeviceNotificationSubscription, isMobileApp, ready]);

  if (!isTellMorePage && (hasCampaign || hasNewsletters || hasTellMore)) {
    return <Redirect to={routeConfig.tellMore.getLink()} />;
  }

  if (
    !isTellMorePage ||
    campaignIsLoading ||
    tellMoreIsLoading ||
    newslettersAreLoading
  ) {
    return null;
  }

  if (hasCampaign) {
    return (
      <ChooseCampaign
        fromSignup={location.hash && location.hash.includes("agir_id")}
        dismiss={dismissCampaign}
      />
    );
  }

  if (hasNewsletters) {
    return <ChooseNewsletters dismiss={dismissNewsletters} />;
  }

  if (hasTellMore) {
    return <TellMore dismiss={dismissTellMore} />;
  }

  if (isMobileApp && hasDeviceNotificationSubscription && !ready) {
    return null;
  }

  if (
    isMobileApp &&
    hasDeviceNotificationSubscription &&
    available &&
    !isSubscribed
  ) {
    return (
      <DeviceNotificationSubscription
        onSubscribe={subscribe}
        onDismiss={dismissDeviceNotificationSubscription}
        subscriptionError={errorMessage}
      />
    );
  }

  return <Redirect to={routeConfig.events.getLink()} />;
};

export default TellMorePage;
