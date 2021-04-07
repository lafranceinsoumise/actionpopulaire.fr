import React, { useCallback, useMemo, useState } from "react";
import { useHistory, useRouteMatch } from "react-router-dom";
import useSWR from "swr";

import {
  getAllNotifications,
  getNotificationStatus,
} from "@agir/notifications/common/notifications.config";
import * as api from "@agir/notifications/common/api";
import { useWebpush } from "@agir/notifications/webpush/subscriptions";

import { ProtectedComponent } from "@agir/front/app/Router";
import NotificationSettingPanel from "./NotificationSettingPanel";

import { routeConfig } from "@agir/front/app/routes.config";

const NotificationSettings = (props) => {
  const { webpushAvailable, isSubscribed, subscribe } = useWebpush();

  const { data: groups } = useSWR("/api/mes-groupes/");
  const { data: userNotifications, mutate } = useSWR(
    api.ENDPOINT.getSubscriptions
  );

  const [isLoading, setIsLoading] = useState(false);

  const notifications = useMemo(() => getAllNotifications(groups), [groups]);

  const activeNotifications = useMemo(
    () => getNotificationStatus(userNotifications),
    [userNotifications]
  );

  const handleChange = useCallback(
    async (notification) => {
      setIsLoading(true);
      let result;
      if (notification.action === "add") {
        result = await api.createSubscriptions(
          notification.activityTypes.map((activityType) => ({
            activityType,
            type: notification.type,
            group: notification.group,
          }))
        );
      }
      if (notification.action === "remove" && notification.subscriptionIds) {
        result = await api.deleteSubscriptions(notification.subscriptionIds);
      }
      setIsLoading(false);
      if (result.error) {
        mutate();
        return;
      }
      mutate((state) =>
        notification.action === "add"
          ? [...state, ...result.data]
          : state.filter(
              (subscription) =>
                !notification.subscriptionIds.includes(subscription.id)
            )
      );
    },
    [mutate]
  );

  return (
    <NotificationSettingPanel
      {...props}
      notifications={notifications}
      activeNotifications={activeNotifications}
      onChange={handleChange}
      disabled={isLoading}
      subscribeDevice={
        webpushAvailable && !isSubscribed ? subscribe : undefined
      }
    />
  );
};

const NotificationSettingRoute = () => {
  const history = useHistory();
  const routeMatch = useRouteMatch(routeConfig.notificationSettings.path);

  const close = useCallback(() => {
    if (routeMatch && routeMatch.params && routeMatch.params.root) {
      history.push(`/${routeMatch.params.root}/`);
    }
  }, [history, routeMatch]);

  return (
    <ProtectedComponent
      Component={NotificationSettings}
      routeConfig={routeConfig.notificationSettings}
      close={close}
      isOpen={!!routeMatch}
    />
  );
};

NotificationSettingRoute.propTypes = {};
export default NotificationSettingRoute;
