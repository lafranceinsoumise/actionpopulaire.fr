import React from "react";

import EventHeader from "./EventHeader";
import { TestConfigProvider } from "@agir/front/genericComponents/Config";
import { DateTime } from "luxon";

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
  argTypes: {
    logged: {
      type: "boolean",
    },
    routes: {
      table: { disable: true },
    },
    date: {
      type: "string",
      control: { type: "date" },
    },
  },
};

const Template = (args) => (
  <EventHeader
    {...{
      ...args,
      date: DateTime.fromMillis(+args.date, { zone: "Europe/Paris" }).setLocale(
        "fr"
      ),
    }}
  />
);

export const Default = Template.bind({});
Default.args = {
  name: "Mon événement",
  date: 1605177480000,
  logged: true,
  routes: { page: "#event", join: "#event/join", cancel: "#event/cancel" },
};
