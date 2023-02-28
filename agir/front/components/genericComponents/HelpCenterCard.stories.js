import React from "react";

import HelpCenterCard from "./HelpCenterCard";

export default {
  component: HelpCenterCard,
  title: "Generic/HelpCenterCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <HelpCenterCard {...args} />;

export const Default = Template.bind({});
Default.args = {};

export const Group = Template.bind({});
Group.args = {
  type: "group",
};

export const Event = Template.bind({});
Event.args = {
  type: "event",
};
