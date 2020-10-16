import React from "react";

import EventHeader from "./EventHeader";
import { TestConfigProvider } from "@agir/front/genericComponents/Config";
import { DateTime } from "luxon";

const routes = { logIn: "#login", signIn: "#signin" };

const defaultStartTime = DateTime.local().plus({ days: 2 });
const defaultEndTime = defaultStartTime.plus({ hours: 2 });

export default {
  component: EventHeader,
  title: "Events/EventHeader",
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
      startTime: DateTime.fromMillis(+args.startTime, {
        zone: "Europe/Paris",
      }).setLocale("fr"),
    }}
  />
);

export const Default = Template.bind({});
Default.args = {
  name: "Mon événement",
  startTime: defaultStartTime.toMillis(),
  endTime: defaultEndTime.toMillis(),
  logged: true,
  routes: { page: "#event", join: "#event/join", cancel: "#event/cancel" },
};
