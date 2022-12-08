import React from "react";

import { Theme } from "@agir/donations/common/StyledComponents";
import SelectedGroupWidget from "./SelectedGroupWidget";

import GROUPS from "@agir/front/mockData/groups";

export default {
  component: SelectedGroupWidget,
  title: "Donations/SelectedGroupWidget",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => (
  <Theme>
    <SelectedGroupWidget {...args} />
  </Theme>
);

export const Default = Template.bind({});
Default.args = {
  isReady: true,
};

export const WithGroup = Template.bind({});
WithGroup.args = {
  ...Default.args,
  group: GROUPS[1],
};

export const WithGroupChoices = Template.bind({});
WithGroupChoices.args = {
  ...WithGroup.args,
  groups: GROUPS,
};

export const WithOnlyOneGroupChoice = Template.bind({});
WithOnlyOneGroupChoice.args = {
  ...WithGroup.args,
  groups: GROUPS.slice(0, 1),
};
