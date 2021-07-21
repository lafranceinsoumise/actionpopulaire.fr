import React from "react";

import Toast from "./Toast";

export default {
  component: Toast,
  title: "Generic/Toast",
  argTypes: {
    $color: {
      control: "color",
    },
  },
};

const Template = (args) => <Toast {...args} />;

export const Default = Template.bind({});
Default.args = {
  children: "Ceci est un toast",
  $color: undefined,
};
