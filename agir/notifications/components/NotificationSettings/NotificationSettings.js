import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useMatch } from "react-router-dom";
import useSWR from "swr";

import {
  getAllNotifications,
  getNotificationStatus,
} from "@agir/notifications/common/notifications.config";
import * as api from "@agir/notifications/common/api";
import { usePush } from "@agir/notifications/push/subscriptions";

import NotificationSettingPanel from "./NotificationSettingPanel";

import { ProtectedComponent } from "@agir/front/app/Router";
import { routeConfig } from "@agir/front/app/routes.config";

const NotificationSettings = (props) => {
  const {
    ready: pushIsReady,
    available,
    isSubscribed,
    subscribe,
    unsubscribe,
    errorMessage,
  } = usePush();

  const { data: groupData } = useSWR("/api/groupes/");
  const {
    data: userNotifications,
    mutate,
    isValidating,
  } = useSWR(api.ENDPOINT.getSubscriptions);

  const [isLoading, setIsLoading] = useState(false);

  const notifications = useMemo(
    () => getAllNotifications(groupData?.groups),
    [groupData]
  );

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

  useEffect(() => {
    mutate();
  }, [mutate, isSubscribed]);

  return (
    <NotificationSettingPanel
      {...props}
      notifications={notifications}
      activeNotifications={activeNotifications}
      onChange={handleChange}
      disabled={isLoading || isValidating}
      ready={!!userNotifications && !!groupData}
      subscribeDevice={available && !isSubscribed ? subscribe : undefined}
      unsubscribeDevice={available && isSubscribed ? unsubscribe : undefined}
      isPushAvailable={available}
      subscriptionError={errorMessage}
      pushIsReady={pushIsReady}
    />
  );
};

const NotificationSettingRoute = () => {
  const navigate = useNavigate();
  const routeMatch = useMatch(routeConfig.notificationSettings.path);

  const close = useCallback(() => {
    if (routeMatch && routeMatch.params && routeMatch.params.root) {
      navigate(`/${routeMatch.params.root}/`);
    }
  }, [navigate, routeMatch]);

  return (
    <ProtectedComponent
      Component={NotificationSettings}
      route={routeConfig.notificationSettings}
      close={close}
      isOpen={!!routeMatch}
    />
  );
};

NotificationSettingRoute.propTypes = {};
export default NotificationSettingRoute;
