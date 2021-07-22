import React from "react";

import HomeActions from "./HomeActions";

export default {
  component: HomeActions,
  title: "app/Home/Actions",
};

const Template = (args) => <HomeActions {...args} />;
export const Default = Template.bind({});
Default.args = {};
