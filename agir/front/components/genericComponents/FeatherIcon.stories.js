import React from "react";
import FeatherIcon, { allIcons } from "./FeatherIcon";

export default {
  component: FeatherIcon,
  title: "FeatherIcon",
  argTypes: {
    name: {
      control: {
        type: "select",
        options: allIcons,
      },
    },
  },
};

const Template = (args) => <FeatherIcon {...args} />;

export const Default = Template.bind({});
Default.args = {
  name: "user",
};

export const Small = Template.bind({});
Small.args = {
  ...Default.args,
  type: "small",
};
