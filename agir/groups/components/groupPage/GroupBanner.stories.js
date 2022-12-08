import React from "react";

import group from "@agir/front/mockData/group.json";

import GroupBanner from "./GroupBanner";

const groupTypes = [
  "Groupe local",
  "Groupe thématique",
  "Groupe fonctionnel",
  "Groupe professionel",
  "Groupe d'action",
];

export default {
  component: GroupBanner,
  title: "Group/GroupBanner",
  argTypes: {
    type: {
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
  type: "Groupe local",
};

export const NoMap = Template.bind({});
NoMap.args = {
  ...group,
  location: {
    ...location,
    coordinates: null,
  },
};
