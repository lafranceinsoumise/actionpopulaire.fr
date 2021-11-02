import React from "react";

import FollowerActions from "./FollowerActions";

export default {
  component: FollowerActions,
  title: "Group/GroupUserActions/FollowerActions",
};

const Template = (args) => <FollowerActions {...args} />;

export const Default = Template.bind({});
Default.args = {
  isLoading: false,
};
