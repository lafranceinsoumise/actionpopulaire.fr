import React from "react";

import { GENDER } from "@agir/lib/utils/display";

import GroupMember from "./GroupMember.js";

export default {
  component: GroupMember,
  title: "Group/GroupMember",
  parameters: {
    layout: "centered",
  },
  argTypes: {
    gender: {
      control: {
        type: "radio",
        options: Object.values(GENDER),
      },
    },
  },
};

const Template = (args) => <GroupMember {...args} />;

export const Member = Template.bind({});
Member.args = {
  name: "Clément Verde",
  email: "admin@example.fr",
  membershipType: 10,
  image: "https://www.fillmurray.com/200/200",
};

export const Manager = Template.bind({});
Manager.args = {
  ...Member.args,
  membershipType: 50,
  image: "https://www.fillmurray.com/200/200",
};

export const Referent = Template.bind({});
Referent.args = {
  ...Member.args,
  membershipType: 100,
  image: "https://www.fillmurray.com/200/200",
};
