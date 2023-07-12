import PropTypes from "prop-types";
import React, { useMemo } from "react";

import CONFIG from "@agir/front/app/Navigation/navigation.config";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes, getUser } from "@agir/front/globalContext/reducers";
import { useUnreadMessageCount } from "@agir/msgs/common/hooks";
import { useUnreadActivityCount } from "@agir/activity/common/hooks";

import SideBar from "./SideBar";
import SecondaryMenu from "./SecondaryMenu";

export const SecondarySideBar = () => (
  <SecondaryMenu
    title="LIENS"
    links={CONFIG.secondaryLinks}
    style={{ padding: 0 }}
  />
);

const ConnectedSideBar = (props) => {
  const unreadActivityCount = useUnreadActivityCount();
  const unreadMessageCount = useUnreadMessageCount();
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);

  const userRoutes = useMemo(
    () =>
      user && user?.groups.length > 0
        ? {
            ...routes,
            userGroups: user.groups.map((group) => ({
              id: group.id,
              label: group.name,
              to: group.link,
            })),
          }
        : routes,
    [user, routes],
  );

  return (
    <SideBar
      {...props}
      unreadActivityCount={unreadActivityCount}
      unreadMessageCount={unreadMessageCount}
      routes={userRoutes}
    />
  );
};

export default ConnectedSideBar;
