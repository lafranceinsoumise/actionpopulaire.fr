import React from "react";

import Skeleton from "./Skeleton";

export default {
  component: Skeleton,
  title: "Generic/Skeleton",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <Skeleton {...args} />;

export const Default = Template.bind({});
Default.args = {
  boxes: 3,
};
