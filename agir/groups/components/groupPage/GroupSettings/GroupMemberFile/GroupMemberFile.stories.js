import React from "react";

import member from "@agir/front/mockData/groupMember.json";
import GroupMemberFile from "./GroupMemberFile.js";

export default {
  component: GroupMemberFile,
  title: "GroupSettings/GroupMemberFile/GroupMemberFile",
  parameters: {
    layout: "padded",
    controls: { expanded: false },
  },
};

const Template = (args) => <GroupMemberFile {...args} />;

export const Default = Template.bind({});
Default.args = {
  member,
  isReferent: true,
};
