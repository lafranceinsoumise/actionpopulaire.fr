import React, { useCallback, useMemo, useState } from "react";
import { useHistory, useRouteMatch } from "react-router-dom";
import useSWR from "swr";

import {
  getAllNotifications,
  getNotificationStatus,
} from "@agir/notifications/common/notifications.config";

import { ProtectedComponent } from "@agir/front/app/Router";
import NotificationSettingPanel from "./NotificationSettingPanel";

import { routeConfig } from "@agir/front/app/routes.config";

const mock = [
  {
    activityType: "group-invitation",
    type: "push",
  },
  {
    activityType: "waiting-payment",
    type: "push",
  },
  {
    activityType: "new-event-aroundme",
    type: "push",
  },
  {
    activityType: "new-event-aroundme",
    type: "email",
  },
  {
    activityType: "group-creation-confirmation",
    group: "bcc310b7-1a20-4746-9945-1e82843308a1",
    type: "email",
  },
];

const NotificationSettings = (props) => {
  const { data: groups } = useSWR("/api/mes-groupes/");
  // const { data: userNotifications } = useSWR("/api/notifications/");

  const [userNotifications, setUserNotifications] = useState(mock);

  const notifications = useMemo(() => getAllNotifications(groups), [groups]);

  const activeNotifications = useMemo(
    () => getNotificationStatus(userNotifications),
    [userNotifications]
  );

  const handleChange = useCallback((notification) => {
    setUserNotifications((state) => {
      if (notification.action === "add") {
        return [
          ...state,
          ...notification.activityTypes.map((activityType) => ({
            activityType,
            type: notification.type,
            group: notification.group,
          })),
        ];
      }
      if (notification.action === "remove") {
        return state.filter((activeNotification) => {
          if (
            activeNotification.type === notification.type &&
            notification.activityTypes.includes(activeNotification.activityType)
          ) {
            return false;
          }
          return true;
        });
      }
      return state;
    });
  }, []);

  return (
    <NotificationSettingPanel
      {...props}
      notifications={notifications}
      activeNotifications={activeNotifications}
      onChange={handleChange}
    />
  );
};

const NotificationSettingRoute = () => {
  const history = useHistory();
  const routeMatch = useRouteMatch(routeConfig.notificationSettings.pathname);

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
