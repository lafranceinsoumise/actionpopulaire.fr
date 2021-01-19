import React from "react";

import EventInfoCard from "./EventInfoCard";

export default {
  component: EventInfoCard,
  title: "Events/EventInfo",
};

const Template = (args) => <EventInfoCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  groups: [
    {
      id: "a",
      name: "Groupe Serge",
    },
    {
      id: "b",
      name: "Groupe Mario",
    },
    {
      id: "c",
      name: "Groupe Daisy",
    },
  ],
  participantCount: 6,
};
