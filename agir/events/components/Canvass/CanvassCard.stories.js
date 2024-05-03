import React from "react";

import CanvassCard from "./CanvassCard";

export default {
  component: CanvassCard,
  title: "Events/Canvass/CanvassCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <CanvassCard {...args} />;

export const Default = Template.bind({});
Default.args = {};

export const Flex = Template.bind({});
Flex.args = {
  flex: true,
};
