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
      displayName: "Foo Bar",
      email: "admin@example.fr",
      membershipType: 5,
      image: "https://loremflickr.com/200/200",
      created: "2020-01-01 00:00:00",
      updated: "2020-01-01 00:00:00",
    },
    {
      id: 1,
      displayName: "Bar Baz",
      email: "admin@example.fr",
      membershipType: 10,
      image: "https://loremflickr.com/200/200",
      created: "2021-01-01 00:00:00",
      updated: "2021-01-01 00:00:00",
    },
    {
      id: 2,
      displayName: "Baz Qux",
      email: "admin@example.fr",
      membershipType: 50,
      image: "https://loremflickr.com/200/200",
      created: "2022-01-01 00:00:00",
      updated: "2022-01-01 00:00:00",
      onResetMembershipType: console.log,
    },
    {
      id: 3,
      displayName: "Qux Quux",
      email: "admin@example.fr",
      membershipType: 100,
      image: "https://loremflickr.com/200/200",
      created: "2023-01-01 00:00:00",
      updated: "2023-01-01 00:00:00",
    },
  ],
};

export const WithAddButton = Template.bind({});
WithAddButton.args = {
  ...Default.args,
  addButtonLabel: "Ajouter votre binôme",
};

export const SortableAndSearchable = Template.bind({});
SortableAndSearchable.args = {
  ...Default.args,
  sortable: true,
  searchable: true,
};
