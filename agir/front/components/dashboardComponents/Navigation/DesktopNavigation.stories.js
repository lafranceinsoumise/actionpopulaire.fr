import React from "react";
import DesktopNavigation, { SecondaryNavigation } from "./DesktopNavigation";

import routes from "@agir/front/mockData/routes";

export default {
  component: DesktopNavigation,
  title: "Navigation/Desktop",
  parameters: {
    layout: "padded",
  },
};

export const Main = () => (
  <DesktopNavigation
    active="events"
    routes={routes}
    unreadMessageCount={2}
    unreadActivityCount={200}
  />
);

export const Secondary = () => <SecondaryNavigation />;
