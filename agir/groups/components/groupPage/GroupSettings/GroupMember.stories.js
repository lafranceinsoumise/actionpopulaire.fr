import React from "react";
import GroupMember from "./GroupMember.js";

export default {
  component: GroupMember,
  title: "Group/GroupMember",
};

const Template = (args) => <GroupMember {...args} />;

export const Default = Template.bind({});

Default.args = {
  name: "Nom Prénom",
  role: "Administratrice",
  email: "admin@example.fr",
  assets: [
    "Blogueur",
    "Blogueur",
    "Blogueur",
    "Blogueur",
    "Blogueur",
    "Blogueur",
  ],
};

export const TwoAssets = Template.bind({});
TwoAssets.args = {
  name: "Nom Prénom",
  role: "Administratrice",
  email: "admin@example.fr",
  assets: ["Blogueur", "Blogueur"],
};

export const NoAssets = Template.bind({});
NoAssets.args = {
  name: "Nom Prénom",
  role: "Administratrice",
  email: "admin@example.fr",
};
