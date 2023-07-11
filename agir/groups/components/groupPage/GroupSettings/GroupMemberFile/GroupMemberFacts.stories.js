import React from "react";

import GroupMemberFacts from "./GroupMemberFacts.js";

export default {
  component: GroupMemberFacts,
  title: "GroupSettings/GroupMemberFile/GroupMemberFacts",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <GroupMemberFacts {...args} />;

export const Default = Template.bind({});
Default.args = {
  is2022: true,
  isLiaison: true,
  hasGroupNotifications: true,
};
