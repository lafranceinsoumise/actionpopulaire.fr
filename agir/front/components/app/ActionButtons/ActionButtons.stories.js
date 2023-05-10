import React from "react";

import { ActionButtons } from "./ActionButtons";

export default {
  component: ActionButtons,
  title: "app/ActionButtons",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => (
  <div style={{ padding: "2rem 0" }}>
    <ActionButtons {...args} />
  </div>
);

export const Default = Template.bind({});
Default.args = {};

export const GroupManager = Template.bind({});
GroupManager.args = {
  ...Default.args,
  user: {
    groups: [
      {
        isManager: true,
      },
    ],
  },
};
