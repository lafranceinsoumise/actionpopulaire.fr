import React from "react";

import GroupAdminBar from "./GroupAdminBar";

export default {
  component: GroupAdminBar,
  title: "Group/GroupAdminBar",
};

const Template = (args) => {
  return <GroupAdminBar {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  routes: {
    createEvent: "#createEvent",
    settings: "#settings",
    members: "#members",
    admin: "#admin",
  },
};
