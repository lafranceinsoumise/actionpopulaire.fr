import React from "react";

import group from "@agir/front/mockData/group.json";

import CONFIG from "@agir/donations/common/config";

import AmountStep from "./AmountStep";

export default {
  component: AmountStep,
  title: "Donations/AmountStep",
  argTypes: {
    type: {
      options: Object.keys(CONFIG),
      control: { type: "radio" },
    },
  },
};

const Template = (args) => <AmountStep {...args} />;

export const Default = Template.bind({});
Default.args = {
  isLoading: false,
  error: "",
  hasGroups: false,
};

export const WithGroupLink = Template.bind({});
WithGroupLink.args = {
  ...Default.args,
  type: "LFI",
  hasGroups: true,
};

export const WithGroupDonation = Template.bind({});
WithGroupDonation.args = {
  ...Default.args,
  group,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  isLoading: true,
};

export const WithError = Template.bind({});
WithError.args = {
  ...Default.args,
  error: "Une erreur est survenue !",
};
