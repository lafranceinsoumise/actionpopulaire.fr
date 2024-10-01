import PropTypes from "prop-types";
import React, {useEffect, useMemo} from "react";

import { routeConfig } from "@agir/front/app/routes.config";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getUser,
  getPageTitle,
  getTopBarRightLink,
} from "@agir/front/globalContext/reducers";

import DashboardPageBar from "./DashboardPageBar";
import SecondaryPageBar from "./SecondaryPageBar";
import {askNotificationPermission} from "@agir/notifications/push/android.utils";

const MobileNavBar = (props) => {
  const { path } = props;

  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const user = useSelector(getUser);
  const pageTitle = useSelector(getPageTitle);
  const settingsLink = useSelector(getTopBarRightLink);

  const currentRoute = useMemo(() => {
    return Object.values(routeConfig).find((route) => route.match(path));
  }, [path]);

  const isSecondary = !!user && currentRoute && currentRoute?.id !== "events";

  return isSecondary ? (
    <SecondaryPageBar
      isLoading={!isSessionLoaded}
      settingsLink={user ? settingsLink : null}
      title={pageTitle || currentRoute.label}
      user={user}
    />
  ) : (
    <DashboardPageBar
      isLoading={!isSessionLoaded}
      settingsLink={user ? settingsLink : null}
      user={user}
      hasSearchLink={currentRoute && currentRoute?.id === "events"}
    />
  );
};

MobileNavBar.propTypes = {
  path: PropTypes.string,
};

export default MobileNavBar;
