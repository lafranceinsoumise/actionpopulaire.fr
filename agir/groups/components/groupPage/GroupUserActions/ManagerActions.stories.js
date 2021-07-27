import React from "react";

import group from "@agir/front/mockData/group.json";

import ManagerActions from "./ManagerActions";

export default {
  component: ManagerActions,
  title: "Group/GroupUserActions/ManagerActions",
};

const Template = (args) => <ManagerActions {...args} />;

export const Default = Template.bind({});
Default.args = {
  routes: group.routes,
  groupSettingsLinks: {
    members: "#members",
    general: "#general",
    manage: "#manage",
    finance: "#finance",
    menu: "#menu",
  },
};
