import React from "react";

import PollingStationField from ".";

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
  votingLocation: {
    id: "75119",
    type: "commune",
  },
};

export const Abroad = Template.bind({});
Abroad.args = {
  name: "polling-station",
  votingLocation: {
    id: "12345",
    type: "consulate",
  },
};
