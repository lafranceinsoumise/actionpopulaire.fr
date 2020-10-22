import React from "react";

import EventGroupCard from "./EventGroupCard";

export default {
  component: EventGroupCard,
  title: "Events/GroupCard",
};

const Template = (args) => <EventGroupCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  name: "Prout",
  url: "https://lafranceinsoumise.fr",
  description: "MegaProut",
  eventCount: 10,
  membersCount: 3,
  typeLabel: "Groupe fonctionnel",
  labels: ["Groupe certifié", "Espace opérationnel"],
};
