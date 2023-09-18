import React from "react";

import SpendingRequestHelp, { HELP_CONFIG } from "./SpendingRequestHelp";

export default {
  component: SpendingRequestHelp,
  title: "Donations/SpendingRequest/SpendingRequestHelp",
  argTypes: {
    onChange: { table: { disable: true } },
  },
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <SpendingRequestHelp {...args} />;

export const Default = Template.bind({});
Default.args = {
  helpId: Object.keys(HELP_CONFIG)[0],
};
