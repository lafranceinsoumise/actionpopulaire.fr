import React from "react";
import Header from "./Header";

export default {
  component: Header,
  title: "Layout/Header",
};

const Template = (args) => <Header {...args} />;

export const Default = Template.bind({});
Default.args = {};
