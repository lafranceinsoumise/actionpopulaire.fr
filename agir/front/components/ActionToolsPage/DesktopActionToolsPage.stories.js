import React from "react";

import DesktopActionToolsPage from "./DesktopActionToolsPage";

export default {
  component: "DesktopActionToolsPage",
  title: "ActionToolsPage/Layout/Desktop",
};

const Template = (args) => <DesktopActionToolsPage {...args} />;

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
