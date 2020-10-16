import React from "react";

import GroupCard from "./GroupCard";

export default {
  component: GroupCard,
  title: "Events/GroupCard",
};

const Template = (args) => <GroupCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  name: "Prout",
  url: "https://lafranceinsoumise.fr",
  description: "MegaProut",
  eventCount: 10,
  membersCount: 3,
  type: "Groupe fonctionnel",
  labels: ["Groupe certifié", "Espace opérationnel"],
};
