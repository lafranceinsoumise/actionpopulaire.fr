import React from "react";

import spendingRequest from "@agir/front/mockData/spendingRequest";
import MobileLayout from "./MobileLayout";

export default {
  component: MobileLayout,
  title: "Donations/SpendingRequest/SpendingRequestDetails/MobileLayout",
};

const Template = (args) => <MobileLayout {...args} />;

export const Default = Template.bind({});
Default.args = {
  spendingRequest,
};

export const AlmostEmpty = Template.bind({});
AlmostEmpty.args = {
  spendingRequest: {
    status: {
      code: "D",
      label: "Brouillon à completer",
      editable: true,
      deletable: true,
    },
    title: spendingRequest.title,
    category: spendingRequest.category,
    group: spendingRequest.group,
  },
};
