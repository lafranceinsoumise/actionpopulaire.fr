import React from "react";

import GroupMemberList from "./GroupMemberList.js";

export default {
  component: GroupMemberList,
  title: "GroupSettings/GroupMemberList",
};

const Template = (args) => (
  <div style={{ padding: "1.5rem" }}>
    <GroupMemberList {...args} />
  </div>
);

export const Default = Template.bind({});
Default.args = {
  members: [
    {
      id: 0,
      displayName: "Clément Verde",
      email: "admin@example.fr",
      membershipType: 5,
      image: "https://www.fillmurray.com/200/200",
    },
    {
      id: 1,
      displayName: "Clément Verde",
      email: "admin@example.fr",
      membershipType: 10,
      image: "https://www.fillmurray.com/200/200",
    },
    {
      id: 2,
      displayName: "Clément Verde",
      email: "admin@example.fr",
      membershipType: 50,
      image: "https://www.fillmurray.com/200/200",
      onResetMembershipType: console.log,
    },
    {
      id: 3,
      displayName: "Clément Verde",
      email: "admin@example.fr",
      membershipType: 100,
      image: "https://www.fillmurray.com/200/200",
    },
  ],
};

export const WithAddButton = Template.bind({});
WithAddButton.args = {
  ...Default.args,
  addButtonLabel: "Ajouter votre binôme",
};
