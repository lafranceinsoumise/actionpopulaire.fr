import React from "react";

import EventHeader from "./EventHeader";
import { TestConfigProvider } from "@agir/front/genericComponents/Config";

const routes = { logIn: "#login", signIn: "#signin" };

export default {
  component: EventHeader,
  title: "Events/Header",
  decorators: [
    (story, { args }) => (
      <TestConfigProvider value={{ user: args.logged ? {} : null, routes }}>
        {story()}
      </TestConfigProvider>
    ),
  ],
  argType: {
    logged: {
      type: "boolean",
    },
    routes: {
      table: { disable: true },
    },
  },
};

const Template = (args) => <EventHeader {...args} />;

export const Default = Template.bind({});
Default.args = {
  name: "Mon événement",
  date: "2020-11-19T12:38+02:00",
  logged: true,
  routes: { page: "#event", join: "#event/join", cancel: "#event/cancel" },
};
