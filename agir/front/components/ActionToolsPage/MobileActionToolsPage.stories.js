import React from "react";

import MobileActionToolsPage from "./MobileActionToolsPage";

export default {
  component: "MobileActionToolsPage",
  title: "ActionToolsPage/Layout/Mobile",
};

const Template = (args) => <MobileActionToolsPage {...args} />;

export const Default = Template.bind({});
Default.args = {
  firstName: "Agathe",
  donationAmount: 100,
  hasGroups: true,
  city: "Le Havre",
  commune: {
    nameOf: "du Havre",
  },
};
