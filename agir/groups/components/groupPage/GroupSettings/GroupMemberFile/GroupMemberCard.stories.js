import React from "react";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";
import { GENDER } from "@agir/lib/utils/display";

import GroupMemberCard from "./GroupMemberCard.js";

const membershipTypeOptions = Object.entries(MEMBERSHIP_TYPES).reduce(
  (options, [key, value]) => ({
    ...options,
    [value]: key,
  }),
  {}
);

const genderOptions = Object.entries(GENDER).reduce(
  (options, [key, value]) => ({
    ...options,
    [value]: key,
  }),
  {}
);

export default {
  component: GroupMemberCard,
  title: "GroupSettings/GroupMemberFile/GroupMemberCard",
  parameters: {
    layout: "padded",
  },
  argTypes: {
    gender: {
      options: Object.keys(genderOptions),
      control: {
        type: "radio",
        labels: genderOptions,
      },
    },
    membershipType: {
      options: Object.keys(membershipTypeOptions),
      control: {
        type: "radio",
        labels: membershipTypeOptions,
      },
    },
  },
};

const Template = (args) => <GroupMemberCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  id: 12345,
  displayName: "JJJ",
  firstName: "Jane Alice",
  lastName: "Doe",
  gender: "O",
  image: "https://www.fillmurray.com/200/200",
  email: "janedoe@agir.local",
  phone: "+336400000000",
  address: "25 passage Dubail, 75010 Paris",
  created: "2020-01-01 00:00:00",
  membershipType: MEMBERSHIP_TYPES.MEMBER,
  subscriber: "John Doe",
  meta: {
    description: "Animateur·ice de groupe d'action",
    group_id: "12345",
    group_name: "Groupe d'action des îles Kerguelen",
  },
};

export const WithoutPersonalDataConsent = Template.bind({});
WithoutPersonalDataConsent.args = {
  id: 12345,
  displayName: "LeTigreDu93",
  email: "letigredu93@agir.local",
  created: "2020-01-01 00:00:00",
  membershipType: MEMBERSHIP_TYPES.MEMBER,
  subscriber: "John Doe",
};
