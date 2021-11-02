import React from "react";

import EditMembershipDialog from "./EditMembershipDialog";

export default {
  component: EditMembershipDialog,
  title: "Group/GroupUserActions/EditMembershipDialog",
};

const Template = (args) => <EditMembershipDialog {...args} />;

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  personalInfoConsent: true,
  isLoading: true,
};
