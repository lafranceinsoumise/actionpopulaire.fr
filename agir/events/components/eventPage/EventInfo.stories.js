import React from "react";

import EventInfo from "./EventInfo";

export default {
  component: EventInfo,
  title: "Events/EventInfo",
};

const Template = (args) => <EventInfo {...args} />;

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
