import React from "react";

import group from "@agir/front/mockData/group.json";

import FollowGroupDialog from "./FollowGroupDialog";

export default {
  component: FollowGroupDialog,
  title: "Group/GroupUserActions/FollowGroupDialog",
};

const Template = (args) => {
  return <FollowGroupDialog {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  groupName: group.name,
};
