import React from "react";
import SideBar, { SecondaryNavigation } from "./SideBar";

import routes from "@agir/front/mockData/routes";

export default {
  component: SideBar,
  title: "Navigation/SideBar",
  parameters: {
    layout: "padded",
  },
};

export const Main = () => (
  <SideBar
    active="events"
    routes={routes}
    unreadMessageCount={2}
    unreadActivityCount={200}
  />
);

export const Secondary = () => <SecondaryNavigation />;
