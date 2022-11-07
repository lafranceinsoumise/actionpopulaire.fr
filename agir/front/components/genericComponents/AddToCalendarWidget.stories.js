import React from "react";

import events from "@agir/front/mockData/events";

import AddToCalendarWidget from "@agir/front/genericComponents/AddToCalendarWidget";

export default {
  component: AddToCalendarWidget,
  title: "Events/EventPage/AddToCalendarWidget",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => <AddToCalendarWidget {...args} />;

export const Default = Template.bind({});
Default.args = {
  ...events[0],
};
