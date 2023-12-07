import React from "react";

import DonationAnnouncement from "./DonationAnnouncement";

export default {
  component: DonationAnnouncement,
  title: "Activities/Announcement/DonationAnnouncement",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => {
  return <DonationAnnouncement {...args} />;
};

export const Default = Template.bind({});
Default.args = {};
