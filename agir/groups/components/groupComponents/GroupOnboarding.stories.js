import React from "react";

import GroupOnboarding from "./GroupOnboarding";

export default {
  component: GroupOnboarding,
  title: "Groupes/GroupOnboarding",
  argTypes: {
    routes: { table: { disable: true } },
  },
  decorators: [
    (story) => (
      <div style={{ margin: "1em", maxWidth: "800px" }}>{story()}</div>
    ),
  ],
};

const Template = GroupOnboarding;

export const Default = Template.bind({});
Default.args = {
  type: "thematic",
  routes: {
    createGroup: "#createGroup",
    groupMapPage: "#groupMapPage",
    thematicTeams: "#thematicTeams",
  },
};
