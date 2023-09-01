import React from "react";

import spendingRequest from "@agir/front/mockData/spendingRequest";
import SpendingRequestDetails from "./SpendingRequestDetails";

export default {
  component: SpendingRequestDetails,
  title: "Donations/SpendingRequest/SpendingRequestDetails",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <SpendingRequestDetails {...args} />;

export const Default = Template.bind({});
Default.args = {
  spendingRequest,
};

export const AlmostEmpty = Template.bind({});
AlmostEmpty.args = {
  spendingRequest: {
    status: "Brouillon à compléter",
    title: spendingRequest.title,
    category: spendingRequest.category,
    group: spendingRequest.group,
    editable: true,
  },
};
