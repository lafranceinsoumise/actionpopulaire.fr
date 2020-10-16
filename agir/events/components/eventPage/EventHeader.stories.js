import React from "react";
import { DateTime } from "luxon";

import EventHeader from "./EventHeader";
import { TestConfigProvider } from "@agir/front/genericComponents/Config";

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
    startTime: {
      type: "string",
      control: { type: "date" },
    },
    endTime: {
      type: "string",
      control: { type: "date" },
    },
    routes: {
      table: { disable: true },
    },
    options: {
      table: { disable: true },
    },
    rsvp: {
      table: { disable: true },
    },
  },
};

const Template = ({ startTime, price, rsvped, ...args }) => (
  <EventHeader
    {...args}
    startTime={DateTime.fromMillis(+startTime, {
      zone: "Europe/Paris",
    }).setLocale("fr")}
    options={{ price }}
    rsvp={rsvped ? { id: "prout" } : null}
  />
);

export const Default = Template.bind({});
Default.args = {
  name: "Mon événement",
  startTime: defaultStartTime.toMillis(),
  endTime: defaultEndTime.toMillis(),
  logged: true,
  price: null,
  routes: {
    page: "#page",
    join: "#join",
    cancel: "#cancel",
  },
};
