import React from "react";

import PollingStationField from "./PollingStationField";

export default {
  component: PollingStationField,
  title: "VotingProxies/PollingStationField",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => {
  return <PollingStationField {...args} />;
};

export const French = Template.bind({});
French.args = {
  name: "polling-station",
  isAbroad: false,
};

export const Abroad = Template.bind({});
Abroad.args = {
  name: "polling-station",
  isAbroad: true,
};
