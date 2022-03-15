import React from "react";

import TokTokCard from "./TokTokCard";

export default {
  component: TokTokCard,
  title: "Events/TokTok/TokTokCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <TokTokCard {...args} />;

export const Default = Template.bind({});
Default.args = {};

export const Flex = Template.bind({});
Flex.args = {
  flex: true,
};
