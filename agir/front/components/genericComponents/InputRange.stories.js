import React from "react";

import InputRange from "./InputRange";

export default {
  component: InputRange,
  title: "InputRange",
};

const Template = (args) => <InputRange {...args} />;

export const Default = Template.bind({});
Default.args = {
  value: 40,
  minValue: 0,
  maxValue: 100,
  step: 1,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
};
