import React from "react";
import { DateTime } from "luxon";

import EventHeader from "./EventHeader";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import {
  scheduleFromStartTimeAndDuration,
  decorateArgs,
} from "@agir/lib/utils/storyUtils";

const routes = { login: "#login", join: "#signin" };

const defaultStartTime = DateTime.local().plus({ days: 2 });

export default {
  component: EventHeader,
  title: "Events/EventPage/EventHeader",
  decorators: [
    (story, { args }) => (
      <TestGlobalContextProvider
        value={{ user: args.logged ? {} : null, routes }}
      >
        <div style={{ margin: "1rem" }}>{story()}</div>
      </TestGlobalContextProvider>
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
    routes: {
      table: { disable: true },
    },
    options: {
      table: { disable: true },
    },
    rsvp: {
      table: { disable: true },
    },
    schedule: {
      table: { disable: true },
    },
  },
};

const Template = decorateArgs(
  scheduleFromStartTimeAndDuration(),
  ({ price, rsvped, ...args }) => {
    return (
      <EventHeader
        {...args}
        options={price !== "" ? { price } : {}}
        rsvp={rsvped ? { id: "prout" } : null}
      />
    );
  }
);

export const Default = Template.bind({});
Default.args = {
  name: "Mon événement",
  startTime: defaultStartTime.toMillis(),
  duration: 2,
  logged: true,
  price: "",
  routes: {
    page: "#page",
    join: "#join",
    cancel: "#cancel",
  },
  rsvped: true,
};

export const NotLogged = Template.bind({});
Default.args = {
  name: "Mon événement",
  startTime: defaultStartTime.toMillis(),
  duration: 2,
  logged: false,
  price: "",
  routes: {
    page: "#page",
    join: "#join",
    cancel: "#cancel",
  },
  rsvped: true,
};

export const NoRSVP = Template.bind({});
Default.args = {
  name: "Mon événement",
  startTime: defaultStartTime.toMillis(),
  duration: 2,
  logged: true,
  price: "",
  routes: {
    page: "#page",
    join: "#join",
    cancel: "#cancel",
  },
  rsvped: false,
};

export const isOnline = Template.bind({});
Default.args = {
  name: "Mon événement en ligne",
  startTime: defaultStartTime.toMillis(),
  duration: 2,
  logged: true,
  price: "",
  routes: {
    page: "#page",
    join: "#join",
    cancel: "#cancel",
  },
  rsvped: true,
  visioConf: "https://actionpopulaire.fr",
};
