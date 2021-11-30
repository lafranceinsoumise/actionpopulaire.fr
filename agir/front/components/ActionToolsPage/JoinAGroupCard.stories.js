import React from "react";

import { JoinAGroupCard } from "./JoinAGroupCard";

export default {
  component: JoinAGroupCard,
  title: "ActionToolsPage/JoinAGroupCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <JoinAGroupCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  city: "Le Havre",
  commune: {
    nameOf: "du Havre",
  },
};
