import React from "react";

import DiscussionAnnouncement from "./DiscussionAnnouncement";

export default {
  component: DiscussionAnnouncement,
  title: "Group/DiscussionAnnouncement",
};

const Template = (args) => {
  return <DiscussionAnnouncement {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  isActive: true,
};
