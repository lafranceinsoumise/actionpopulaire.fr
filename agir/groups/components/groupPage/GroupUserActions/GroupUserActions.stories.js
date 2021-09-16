import React from "react";

import group from "@agir/front/mockData/group.json";

import GroupUserActions from "./GroupUserActions";

export default {
  component: GroupUserActions,
  title: "Group/GroupUserActions/Wrapper",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => {
  return <GroupUserActions {...args} />;
};

export const Anonymous = Template.bind({});
Anonymous.args = {
  id: group.id,
  routes: group.routes,
  groupSettingsLinks: {
    members: "#members",
    general: "#general",
    manage: "#manage",
    finance: "#finance",
    menu: "#menu",
  },
  isAuthenticated: false,
  isMember: false,
  isActiveMember: false,
  isManager: false,
};

export const NonMember = Template.bind({});
NonMember.args = {
  ...Anonymous.args,
  isAuthenticated: true,
};

export const Follower = Template.bind({});
Follower.args = {
  ...NonMember.args,
  isMember: true,
};

export const Member = Template.bind({});
Member.args = {
  ...Follower.args,
  isActiveMember: true,
};

export const Manager = Template.bind({});
Manager.args = {
  ...Member.args,
  isManager: true,
};
