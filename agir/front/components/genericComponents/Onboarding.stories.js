import React from "react";

import Onboarding from "./Onboarding";

export default {
  component: Onboarding,
  title: "generic/Onboarding",
  argTypes: {
    routes: { table: { disable: true } },
  },
  decorators: [
    (story) => (
      <div style={{ margin: "1em", maxWidth: "800px" }}>{story()}</div>
    ),
  ],
};

const Template = (args) => <Onboarding {...args} />;

export const Default = Template.bind({});
Default.args = {
  type: "group__action",
  routes: {
    createGroup: "#createGroup",
    createEvent: "#createEvent",
    groupMapPage: "#groupMapPage",
    eventMapPage: "#eventMapPage",
    thematicTeams: "#thematicTeams",
    newGroupHelp: "#newGroupHelp",
  },
};
