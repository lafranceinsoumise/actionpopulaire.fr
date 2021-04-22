import React from "react";

import Panel from "./Panel";

export default {
  component: Panel,
  title: "Generic/Panel",
};

const Template = (args) => <Panel {...args} />;

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  children: "Content",
  noScroll: true,
  position: "right",
  title: "Title",
};
