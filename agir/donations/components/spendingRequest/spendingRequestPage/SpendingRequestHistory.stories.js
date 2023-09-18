import React from "react";

import spendingRequest from "@agir/front/mockData/spendingRequest";
import SpendingRequestHistory from "./SpendingRequestHistory";

export default {
  component: SpendingRequestHistory,
  title: "Donations/SpendingRequest/SpendingRequestHistory",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <SpendingRequestHistory {...args} />;

export const Default = Template.bind({});
Default.args = {
  status: spendingRequest.status,
  history: spendingRequest.history,
};
