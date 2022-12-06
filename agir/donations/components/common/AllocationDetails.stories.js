import React from "react";

import { Theme } from "@agir/donations/common/StyledComponents";
import AllocationDetails from "@agir/donations/common/AllocationDetails";
export default {
  component: AllocationDetails,
  title: "Donations/AllocationDetails",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => (
  <Theme>
    <AllocationDetails {...args} />
  </Theme>
);

export const Default = Template.bind({});
Default.args = {
  totalAmount: 10000,
  byMonth: true,
  groupName: "Belleville insoumise",
  allocations: [
    {
      type: "cns",
      value: 2000,
    },
    {
      type: "group",
      group: "12345",
      value: 2750,
    },
    {
      type: "departement",
      value: 2750,
    },
    {
      type: "national",
      value: 2650,
    },
  ],
};

export const NoGroup = Template.bind({});
NoGroup.args = {
  ...Default.args,
  allocations: [
    {
      type: "cns",
      value: 2000,
    },
    {
      type: "departement",
      value: 2750,
    },
    {
      type: "national",
      value: 2650,
    },
  ],
};

export const NoCNS = Template.bind({});
NoCNS.args = {
  ...NoGroup.args,
  allocations: [
    {
      type: "cns",
      value: 0,
    },
    {
      type: "departement",
      value: 2750,
    },
    {
      type: "national",
      value: 2650,
    },
  ],
};
