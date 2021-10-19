import React from "react";
import BottomBar from "./BottomBar";

import routes from "@agir/front/mockData/routes";

export default {
  component: BottomBar,
  title: "Navigation/BottomBar",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <BottomBar {...args} />;

export const Default = Template.bind({});
Default.args = {
  active: "events",
  unreadMessageCount: 2,
  unreadActivityCount: 100,
};
