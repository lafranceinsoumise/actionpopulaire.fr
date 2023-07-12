import React from "react";
import { DateTime } from "luxon";

import EventHeader from "./EventHeader";

import events from "@agir/front/mockData/events";

import {
  scheduleFromStartTimeAndDuration,
  decorateArgs,
} from "@agir/lib/utils/storyUtils";

const pastStartTime = DateTime.local().minus({ days: 2 });
const upcomingStartTime = DateTime.local().plus({ days: 2 });

export default {
  component: EventHeader,
  title: "Events/EventPage/EventHeader",
  parameters: {
    layout: "padded",
  },
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
  ({ rsvped, ...args }) => {
    return <EventHeader {...args} rsvp={rsvped ? "CO" : ""} />;
  },
);

export const Default = Template.bind({});
Default.args = {
  ...events[0],
  startTime: pastStartTime,
  rsvped: true,
  options: {},
};

export const Upcoming = Template.bind({});
Upcoming.args = {
  ...events[0],
  startTime: upcomingStartTime,
  rsvped: true,
  options: {},
};

export const NoRSVP = Template.bind({});
NoRSVP.args = {
  ...Upcoming.args,
  rsvped: false,
};

export const NORSVPWithPrice = Template.bind({});
NORSVPWithPrice.args = {
  ...Upcoming.args,
  options: { price: "100$" },
};

export const RSVPWithPrice = Template.bind({});
RSVPWithPrice.args = {
  ...Upcoming.args,
  rsvped: true,
  allowGuests: true,
  options: { price: "100$" },
};

export const OnlineEvent = Template.bind({});
OnlineEvent.args = {
  ...Upcoming.args,
  rsvped: true,
  onlineUrl: "https://actionpopulaire.fr",
};
