import React from "react";

import ActionButtons from "./ActionButtons";

export default {
  component: ActionButtons,
  title: "app/ActionButtons",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ActionButtons {...args} />;

export const Default = Template.bind({});
Default.args = {};
