import React from "react";

import group from "./group.json";

import GroupBanner from "./GroupBanner";

const groupTypes = [
  "Groupe local",
  "Groupe thématique",
  "Groupe fonctionnel",
  "Groupe professionel",
  "Équipe de soutien « Nous Sommes Pour ! »",
];

export default {
  component: GroupBanner,
  title: "Group/GroupBanner",
  argTypes: {
    type: {
      defaultValue: "Groupe local",
      control: {
        type: "select",
        required: true,
        options: groupTypes,
      },
    },
  },
};

const Template = (args) => {
  return <GroupBanner {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  ...group,
};
