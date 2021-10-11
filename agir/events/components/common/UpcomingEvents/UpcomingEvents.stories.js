import React from "react";

import UpcomingEvents from "./UpcomingEvents";

import events from "@agir/front/mockData/events";

export default {
  component: UpcomingEvents,
  title: "Events/UpcomingEvents",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => (
  <div>
    <UpcomingEvents {...args} />
  </div>
);

export const Default = Template.bind({});
Default.args = {
  events,
};

export const SingleEvent = Template.bind({});
SingleEvent.args = {
  events: events.slice(0, 1),
};
