import React from "react";

import group from "@agir/front/mockData/group.json";

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
