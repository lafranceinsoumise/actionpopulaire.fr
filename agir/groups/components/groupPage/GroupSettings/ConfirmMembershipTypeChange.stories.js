import React from "react";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

import member from "@agir/front/mockData/groupMember";

import ConfirmMembershipTypeChange from "./ConfirmMembershipTypeChange.js";

export default {
  component: ConfirmMembershipTypeChange,
  title: "GroupSettings/ConfirmMembershipTypeChange",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ConfirmMembershipTypeChange {...args} />;

export const MemberToFollower = Template.bind({});
MemberToFollower.args = {
  selectedMember: {
    ...member,
    membershipType: MEMBERSHIP_TYPES.MEMBER,
  },
  selectedMembershipType: MEMBERSHIP_TYPES.FOLLOWER,
  isLoading: false,
};
export const FollowerToMember = Template.bind({});
FollowerToMember.args = {
  selectedMember: {
    ...member,
    membershipType: MEMBERSHIP_TYPES.FOLLOWER,
  },
  selectedMembershipType: MEMBERSHIP_TYPES.MEMBER,
  isLoading: false,
};
export const MemberToManager = Template.bind({});
MemberToManager.args = {
  selectedMember: {
    ...member,
    membershipType: MEMBERSHIP_TYPES.MEMBER,
  },
  selectedMembershipType: MEMBERSHIP_TYPES.MANAGER,
  isLoading: false,
};
export const ManagerToMember = Template.bind({});
ManagerToMember.args = {
  selectedMember: {
    ...member,
    membershipType: MEMBERSHIP_TYPES.MANAGER,
  },
  selectedMembershipType: MEMBERSHIP_TYPES.MEMBER,
  isLoading: false,
};
