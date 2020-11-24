import React from "react";

import Activities from "@agir/activity/common/Activities";
import RequiredActionCard from "./RequiredActionCard";

import * as RequiredActionCardStories from "./RequiredActionCard.stories";

export default {
  component: Activities,
  title: "Activities/RequiredActivityList",
  argTypes: {},
};

const Template = (args) => {
  return <Activities {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  activities: [
    ...Object.values(RequiredActionCardStories)
      .map(({ args }) => args)
      .filter(Boolean),
  ],
  onDismiss: () => {},
  CardComponent: RequiredActionCard,
};

export const Empty = Template.bind({});
Empty.args = {
  activities: [],
  onDismiss: () => {},
};
