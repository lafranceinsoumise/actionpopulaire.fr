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

export const LessThanTwenty = Template.bind({});
LessThanTwenty.args = {
  value: 1,
  size: 150,
};
export const MoreThanTwenty = Template.bind({});
MoreThanTwenty.args = {
  ...LessThanTwenty.args,
  value: 27,
};
