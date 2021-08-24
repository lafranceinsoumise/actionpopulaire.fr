import React from "react";

import IntroApp from "./IntroApp";

export default {
  component: IntroApp,
  title: "app/IntroApp",
};

const Template = (args) => <IntroApp {...args} />;

export const Default = Template.bind({});
Default.args = {};
