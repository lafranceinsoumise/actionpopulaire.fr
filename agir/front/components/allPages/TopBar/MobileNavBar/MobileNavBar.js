import PropTypes from "prop-types";
import React, { useMemo } from "react";

import { routeConfig } from "@agir/front/app/routes.config";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getUser,
  getPageTitle,
  getBackLink,
  getTopBarRightLink,
} from "@agir/front/globalContext/reducers";

import DashboardPageBar from "./DashboardPageBar";
import SecondaryPageBar from "./SecondaryPageBar";

const MobileNavBar = (props) => {
  const { path } = props;

  const user = useSelector(getUser);
  const pageTitle = useSelector(getPageTitle);
  const backLink = useSelector(getBackLink);
  const settingsLink = useSelector(getTopBarRightLink);

  const currentRoute = useMemo(() => {
    return Object.values(routeConfig).find((route) => route.match(path));
  }, [path]);

  const isSecondary = !!user && currentRoute && currentRoute?.id !== "events";

  return isSecondary ? (
    <SecondaryPageBar
      backLink={backLink}
      settingsLink={user ? settingsLink : null}
      title={pageTitle || currentRoute.label}
      user={user}
    />
  ) : (
    <DashboardPageBar settingsLink={user ? settingsLink : null} user={user} />
  );
};

MobileNavBar.propTypes = {
  path: PropTypes.string,
};

export default MobileNavBar;
