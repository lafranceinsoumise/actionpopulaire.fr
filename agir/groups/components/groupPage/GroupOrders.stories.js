import React from "react";

import group from "@agir/groups/groupPage/group.json";

import GroupOrders from "./GroupOrders";

export default {
  component: GroupOrders,
  title: "Group/GroupOrders",
};

const Template = (args) => {
  return <GroupOrders {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  ...group,
};
