import React from "react";

import StaticToast from "./StaticToast";

export default {
  component: StaticToast,
  title: "Generic/StaticToast",
  argTypes: {
    $color: {
      control: "color",
    },
  },
};

const Template = (args) => <StaticToast {...args} />;

export const Default = Template.bind({});
Default.args = {
  children: "Ceci est un toast statique",
  $color: undefined,
};
