import React from "react";

import { HowTo } from "./HowTo";

export default {
  component: HowTo,
  title: "Events/TokTok/TokTokPreview/HowTo",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <HowTo {...args} />;

export const Default = Template.bind({});
Default.args = {
  isInitiallyCollapsed: false,
};

export const Collapsed = Template.bind({});
Collapsed.args = {
  isInitiallyCollapsed: true,
};
