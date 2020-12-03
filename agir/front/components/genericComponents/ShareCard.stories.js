import React from "react";

import ShareCard from "./ShareCard";

export default {
  component: ShareCard,
  title: "Generic/Share",
};

const Template = (args) => <ShareCard {...args} />;

export const Default = Template.bind({});
Default.args = {};
