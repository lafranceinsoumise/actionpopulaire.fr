import React, { useCallback, useMemo, useState } from "react";
import { useHistory, useRouteMatch } from "react-router-dom";
import useSWR from "swr";

import {
  getAllNotifications,
  getNotificationStatus,
  getNewsletterStatus,
} from "@agir/notifications/common/notifications.config";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import * as api from "@agir/notifications/common/api";

import NotificationSettingPanel from "./NotificationSettingPanel";

import { ProtectedComponent } from "@agir/front/app/Router";
import { routeConfig } from "@agir/front/app/routes.config";
import { updateProfile } from "@agir/front/authentication/api";

const NotificationSettings = (props) => {
  const {
    data: userNotifications,
    mutate,
    isValidating,
  } = useSWR(api.ENDPOINT.getSubscriptions);

  const user = useSelector(getUser);
  const [isLoading, setIsLoading] = useState(false);

  const { data: profile, mutate: mutateProfile } = useSWR("/api/user/profile/");

  const notifications = useMemo(() => getAllNotifications(user), [user]);

  const allActiveNotifications = useMemo(
    () => ({
      ...getNewsletterStatus(profile?.newsletters),
      ...getNotificationStatus(userNotifications),
    }),
    [profile, userNotifications],
  );

  const handleChange = useCallback(
    async (notification) => {
      setIsLoading(true);
      let result;

      // Update profile newsletters
      if ("isNewsletter" in notification && !!profile) {
        const newsletters =
          notification.action === "add"
            ? [...profile.newsletters, notification.id]
            : profile.newsletters.filter((notif) => notif !== notification.id);

        result = await updateProfile({ newsletters });
        setIsLoading(false);
        mutateProfile(
          (userProfile) => result?.data || { ...userProfile, newsletters },
          false,
        );
        return;
      }

      // Update activities
      if (notification.action === "add") {
        result = await api.createSubscriptions(
          notification.activityTypes.map((activityType) => ({
            activityType,
            type: notification.type,
            group: notification.group,
          })),
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
                !notification.subscriptionIds.includes(subscription.id),
            ),
      );
    },
    [mutate, profile],
  );

  return (
    <NotificationSettingPanel
      {...props}
      notifications={notifications}
      activeNotifications={allActiveNotifications}
      onChange={handleChange}
      disabled={isLoading || isValidating}
      ready={!!userNotifications}
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
      route={routeConfig.notificationSettings}
      close={close}
      isOpen={!!routeMatch}
    />
  );
};

NotificationSettingRoute.propTypes = {};
export default NotificationSettingRoute;
