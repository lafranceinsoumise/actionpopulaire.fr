import React from "react";

import Navigation from "./Navigation";

export default {
  component: Navigation,
  title: "Dashboard/Navigation",
};

const Template = (args) => <Navigation {...args} />;

export const Default = Template.bind({});
Default.args = {
  active: "events",
  routes: {
    events: "#",
    groups: "#",
    notifications: "#",
    menu: "#",
  },
};
