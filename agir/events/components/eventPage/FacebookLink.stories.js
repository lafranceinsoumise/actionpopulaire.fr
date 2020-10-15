import React from "react";

import FacebookLink from "./FacebookLink";

export default {
  component: FacebookLink,
  title: "Events/FacebookLink",
};

const Template = (args) => <FacebookLink {...args} />;

export const Default = Template.bind({});
Default.args = {
  facebookUrl: "https://facebook.com",
};
