import React from "react";

import GroupMemberList from "./GroupMemberList.js";

export default {
  component: GroupMemberList,
  title: "GroupSettings/GroupMemberList",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => <GroupMemberList {...args} />;

export const Default = Template.bind({});
Default.args = {
  members: [
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
