import React from "react";

import Share from "./Share";

export default {
  component: Share,
  title: "Generic/Share",
};

const Template = (args) => <Share {...args} />;

export const Default = Template.bind({});
Default.args = {};
