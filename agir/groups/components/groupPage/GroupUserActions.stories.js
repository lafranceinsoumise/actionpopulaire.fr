import React from "react";

import group from "@agir/front/mockData/group.json";

import GroupUserActions from "./GroupUserActions";

export default {
  component: GroupUserActions,
  title: "Group/GroupUserActions",
};

const Template = (args) => {
  return <GroupUserActions {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  ...group,
  isMember: false,
  isManager: false,
};

export const MemberView = Template.bind({});
MemberView.args = {
  ...group,
  isMember: true,
  isManager: false,
};

export const ManagerView = Template.bind({});
ManagerView.args = {
  ...group,
  isMember: true,
  isManager: true,
};
