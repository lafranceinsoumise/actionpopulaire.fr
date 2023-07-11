import React from "react";

import group from "@agir/front/mockData/group.json";

import { Theme } from "@agir/donations/common/StyledComponents";
import AmountStep from "./AmountStep";
import CONFIG from "@agir/donations/common/config";

export default {
  component: AmountStep,
  title: "Donations/AmountStep",
  argTypes: { selectGroup: { action: "selectGroup" } },
};

const Template = (args) => (
  <Theme>
    <AmountStep {...args} />
  </Theme>
);

export const Default = Template.bind({});
Default.args = {
  ...CONFIG.default,
  isLoading: false,
  error: "",
  hasGroups: false,
};

export const WithGroupLink = Template.bind({});
WithGroupLink.args = {
  ...Default.args,
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
