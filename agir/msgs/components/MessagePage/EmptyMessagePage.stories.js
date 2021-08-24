import React from "react";

import EmptyMessagePage from "./EmptyMessagePage";

export default {
  component: EmptyMessagePage,
  title: "Messages/MessagePage/EmptyMessagePage",
};

const Template = (args) => {
  return <EmptyMessagePage {...args} />;
};

export const Default = Template.bind({});
Default.args = {};
