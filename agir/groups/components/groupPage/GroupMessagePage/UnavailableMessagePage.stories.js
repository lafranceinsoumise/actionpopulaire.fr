import React from "react";

import UnavailableMessagePage from "./UnavailableMessagePage";

export default {
  component: UnavailableMessagePage,
  title: "Group/UnavailableMessagePage",
};

const Template = (args) => {
  return <UnavailableMessagePage {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  groupURL: "#group",
};
