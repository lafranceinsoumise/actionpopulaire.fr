import React from "react";
import CounterBadge from "./CounterBadge";

export default {
  component: CounterBadge,
  title: "Navigation/CounterBadge",
  parameters: {
    layout: "centered",
  },
  argTypes: {
    size: {
      control: {
        type: "number",
      },
    },
  },
};

const Template = ({ size, ...args }) => (
  <CounterBadge
    style={size ? { width: size, height: size } : undefined}
    {...args}
  />
);

export const OneDigit = Template.bind({});
OneDigit.args = {
  value: 1,
  size: 150,
};
export const TwoDigits = Template.bind({});
TwoDigits.args = {
  ...OneDigit.args,
  value: 10,
};
export const ThreeDigits = Template.bind({});
ThreeDigits.args = {
  ...OneDigit.args,
  value: 100,
};
