import React from "react";

import { DonateCard } from "./DonateCard";

export default {
  component: DonateCard,
  title: "ActionToolsPage/DonateCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <DonateCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  amount: 38000000,
};
