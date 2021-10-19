import PropTypes from "prop-types";
import React, { Suspense } from "react";

import { lazy } from "@agir/front/app/utils";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";
import { useUnreadMessageCount } from "@agir/msgs/common/hooks";
import { useUnreadActivityCount } from "@agir/activity/common/hooks";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

export { SecondaryNavigation } from "./DesktopNavigation";

const MobileNavigation = lazy(() => import("./MobileNavigation"));
const DesktopNavigation = lazy(() => import("./DesktopNavigation"));

const Navigation = (props) => {
  const unreadActivityCount = useUnreadActivityCount();
  const unreadMessageCount = useUnreadMessageCount();
  const routes = useSelector(getRoutes);

  const Component = useResponsiveMemo(MobileNavigation, DesktopNavigation);

  return (
    <Suspense fallback={null}>
      <Component
        {...props}
        unreadActivityCount={unreadActivityCount}
        unreadMessageCount={unreadMessageCount}
        routes={routes}
      />
    </Suspense>
  );
};

export default Navigation;
