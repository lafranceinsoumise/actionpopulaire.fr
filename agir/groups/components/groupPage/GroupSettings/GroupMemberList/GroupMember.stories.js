import React from "react";

import { GENDER } from "@agir/lib/utils/display";

import GroupMember from "./GroupMember.js";

export default {
  component: GroupMember,
  title: "GroupSettings/GroupMember",
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
  id: 1,
  displayName: "Clément Verde",
  email: "admin@example.fr",
  membershipType: 10,
  image: "https://loremflickr.com/200/200",
};

export const Follower = Template.bind({});
Follower.args = {
  ...Member.args,
  membershipType: 5,
};

export const Manager = Template.bind({});
Manager.args = {
  ...Member.args,
  membershipType: 50,
};

export const Referent = Template.bind({});
Referent.args = {
  ...Member.args,
  membershipType: 100,
};
