import React from "react";
import TopBar from "./TopBar";

export default {
  component: TopBar,
  title: "Layout/TopBar",
};

const Template = (args) => <TopBar {...args} />;

export const Default = Template.bind({});
Default.args = {};
