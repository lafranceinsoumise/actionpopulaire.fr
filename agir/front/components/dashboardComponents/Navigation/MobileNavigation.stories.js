import React from "react";
import MobileNavigation from "./MobileNavigation";

import routes from "@agir/front/mockData/routes";

export default {
  component: MobileNavigation,
  title: "Navigation/Mobile",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <MobileNavigation {...args} />;

export const Default = Template.bind({});
Default.args = {
  active: "events",
  unreadMessageCount: 2,
  unreadActivityCount: 100,
};
