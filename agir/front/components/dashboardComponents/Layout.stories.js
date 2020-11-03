import React from "react";

import Layout from "./Layout";

export default {
  component: Layout,
  title: "Dashboard/Layout",
};

const Template = (args) => <Layout {...args} />;

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
