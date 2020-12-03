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
      name: "Groupe Serge",
      url: "https://lafranceinsoumise.fr",
    },
    {
      name: "Groupe Mario",
      url: "https://lafranceinsoumise.fr",
    },
    {
      name: "Groupe Daisy",
      url: "https://lafranceinsoumise.fr",
    },
  ],
  participantCount: 6,
};
