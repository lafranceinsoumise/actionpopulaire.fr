import React from "react";

import GroupMemberActions from "./GroupMemberActions.js";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

const membershipTypeOptions = Object.entries(MEMBERSHIP_TYPES).reduce(
  (options, [key, value]) => ({
    ...options,
    [value]: key,
  }),
  {},
);

export default {
  component: GroupMemberActions,
  title: "GroupSettings/GroupMemberFile/GroupMemberActions",
  parameters: {
    layout: "padded",
  },
  argTypes: {
    membershipType: {
      options: Object.keys(membershipTypeOptions),
      control: {
        type: "radio",
        labels: membershipTypeOptions,
      },
    },
  },
};

const Template = (args) => <GroupMemberActions {...args} />;

export const Follower = Template.bind({});
Follower.args = {
  isGroupFull: false,
  currentMembershipType: MEMBERSHIP_TYPES.FOLLOWER,
};
export const Member = Template.bind({});
Member.args = {
  isGroupFull: false,
  currentMembershipType: MEMBERSHIP_TYPES.MEMBER,
};
export const Manager = Template.bind({});
Manager.args = {
  isGroupFull: false,
  currentMembershipType: MEMBERSHIP_TYPES.MANAGER,
  isReferent: true,
};
