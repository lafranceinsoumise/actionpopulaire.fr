import React from "react";

import EventSpeakers from "./EventSpeakers";

export default {
  component: EventSpeakers,
  title: "Events/EventPage/EventSpeakers",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <EventSpeakers {...args} />;

export const Default = Template.bind({});
Default.args = {
  eventSpeakers: [
    {
      name: "Mathilde Panot",
      description: "Députée du 94, présidente du groupe parlementaire",
    },
    {
      name: "Louis Boyard",
      description: "",
    },
    {
      name: "Pierre-Yves Cadalen",
      description: "Co-animateur du livret Constituante",
    },
  ],
};

export const SingleSpeaker = Template.bind({});
SingleSpeaker.args = {
  ...Default.args,
  eventSpeakers: [Default.args.eventSpeakers[0]],
};
