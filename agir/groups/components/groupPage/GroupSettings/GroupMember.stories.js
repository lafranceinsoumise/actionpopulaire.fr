import React from "react";
import GroupMember from "./GroupMember.js";

export default {
  component: GroupMember,
  title: "GroupSettings/Member",
};


const Template = (args) => <GroupMember {...args} />;

export const Default = Template.bind({});
Default.args = {};


