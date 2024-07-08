import React from "react";

import MOCK_GROUPS from "@agir/front/mockData/thematicGroups";
import ThematicGroupCard from "./ThematicGroupCard";

export default {
  component: ThematicGroupCard,
  title: "Generic/ThematicGroupCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ThematicGroupCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  ...MOCK_GROUPS[0],
  image: "https://loremflickr.com/320/320",
};

export const WithoutImage = Template.bind({});
WithoutImage.args = {
  ...Default.args,
  image: null,
};

export const WithoutLink = Template.bind({});
WithoutLink.args = {
  ...Default.args,
  externalLink: null,
};
