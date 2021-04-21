import React, { useCallback, useState } from "react";
import { Redirect, useRouteMatch } from "react-router-dom";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { usePush } from "@agir/notifications/push/subscriptions";
import { routeConfig } from "@agir/front/app/routes.config";
import { useMobileApp } from "@agir/front/app/hooks";

import TellMore from "./TellMore";
import ChooseCampaign from "./ChooseCampaign";
import DeviceNotificationSubscription from "./DeviceNotificationSubscription";

const TellMorePage = () => {
  const isTellMorePage = useRouteMatch(routeConfig.tellMore.getLink());

  const { available, isSubscribed, subscribe, ready, errorMessage } = usePush();
  const [hasCampaign, dismissCampaign] = useCustomAnnouncement(
    "chooseCampaign"
  );
  const [hasTellMore, dismissTellMore] = useCustomAnnouncement("tellMore");
  const [
    hasDeviceNotificationSubscription,
    setHasDeviceNotificationSubscription,
  ] = useState(isTellMorePage);

  const dismissDeviceNotificationSubscription = useCallback(() => {
    setHasDeviceNotificationSubscription(false);
  }, []);

  const { isMobileApp } = useMobileApp();

  if (!isTellMorePage && (hasCampaign || hasTellMore)) {
    return <Redirect to={routeConfig.tellMore.getLink()} />;
  }

  if (hasCampaign) {
    return <ChooseCampaign dismiss={dismissCampaign} />;
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
