import PropTypes from "prop-types";
import React from "react";

import CONFIG from "@agir/front/app/Navigation/navigation.config";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";
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

  return (
    <SideBar
      {...props}
      unreadActivityCount={unreadActivityCount}
      unreadMessageCount={unreadMessageCount}
      routes={routes}
    />
  );
};

export default ConnectedSideBar;
