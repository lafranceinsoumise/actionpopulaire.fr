import React from "react";

import QuitGroupDialog from "./QuitGroupDialog";

export default {
  component: QuitGroupDialog,
  title: "Group/GroupUserActions/QuitGroupDialog",
};

const Template = (args) => <QuitGroupDialog {...args} />;

export const Default = Template.bind({});
Default.args = {
  groupName: "Le groupe d'action de la rue de la Grange aux belles",
  isActiveMember: true,
  shouldShow: true,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  isLoading: true,
};
