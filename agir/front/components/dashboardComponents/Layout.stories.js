import React from "react";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import Layout from "./Layout";

export default {
  component: Layout,
  title: "Dashboard/Layout",
};

const Template = (args) => (
  <TestGlobalContextProvider
    value={{
      routes: args.routes,
      announcements: [],
    }}
  >
    <Layout {...args} />
  </TestGlobalContextProvider>
);

export const Default = Template.bind({});
Default.args = {
  active: "events",
  routes: {
    events: "#",
    groups: "#",
    notifications: "#",
    menu: "#",
  },
  announcements: [],
};
