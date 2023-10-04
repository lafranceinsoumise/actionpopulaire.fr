import React from "react";

import spendingRequest from "@agir/front/mockData/spendingRequest";
import DesktopLayout from "./DesktopLayout";

export default {
  component: DesktopLayout,
  title: "Donations/SpendingRequest/SpendingRequestDetails/DesktopLayout",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <DesktopLayout {...args} />;

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
