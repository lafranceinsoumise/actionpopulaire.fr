import React, { useCallback } from "react";
import { useHistory, useRouteMatch } from "react-router-dom";

import notifications from "@agir/front/mockData/notificationSettings";

import { ProtectedComponent } from "@agir/front/app/Router";
import NotificationSettingPanel from "./NotificationSettingPanel";

import { routeConfig } from "@agir/front/app/routes.config";

const NotificationSettings = (props) => {
  return <NotificationSettingPanel {...props} notifications={notifications} />;
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
