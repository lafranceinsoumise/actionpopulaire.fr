import React from "react";

import MemberActions from "./MemberActions";

export default {
  component: MemberActions,
  title: "Group/GroupUserActions/MemberActions",
};

const Template = (args) => <MemberActions {...args} />;

export const Default = Template.bind({});
Default.args = {};
