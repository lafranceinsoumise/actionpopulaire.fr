import React, { useCallback, useState } from "react";
import { Redirect, useRouteMatch } from "react-router-dom";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { useWebpush } from "@agir/notifications/webpush/subscriptions";
import { routeConfig } from "@agir/front/app/routes.config";

import TellMore from "./TellMore";
import ChooseCampaign from "./ChooseCampaign";
import DeviceNotificationSubscription from "./DeviceNotificationSubscription";

const TellMorePage = () => {
  const isTellMorePage = useRouteMatch(routeConfig.tellMore.getLink());

  const { webpushAvailable, isSubscribed, subscribe, ready } = useWebpush();
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

  if (!isTellMorePage && (hasCampaign || hasTellMore)) {
    return <Redirect to={routeConfig.tellMore.getLink()} />;
  }

  if (hasCampaign) {
    return <ChooseCampaign dismiss={dismissCampaign} />;
  }
  if (hasTellMore) {
    return <TellMore dismiss={dismissTellMore} />;
  }
  if (hasDeviceNotificationSubscription && !ready) {
    return null;
  }
  if (hasDeviceNotificationSubscription && webpushAvailable && !isSubscribed) {
    return (
      <DeviceNotificationSubscription
        onSubscribe={subscribe}
        onDismiss={dismissDeviceNotificationSubscription}
      />
    );
  }

  return <Redirect to={routeConfig.events.getLink()} />;
};

export default TellMorePage;
