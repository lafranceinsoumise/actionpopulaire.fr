import React from "react";

import RequiredActionCard from "./RequiredActionCard";

export default {
  component: RequiredActionCard,
  title: "Activities/RequiredActionCard",
  argTypes: {
    onDismiss: { action: "onDismiss" },
  },
};

const Template = (args) => {
  return (
    <div
      style={{
        maxWidth: 396,
        margin: "10px auto",
      }}
    >
      <RequiredActionCard {...args} />
    </div>
  );
};

export const WaitingPayment = Template.bind({});
WaitingPayment.args = {
  type: "waiting-payment",
  id: 1,
  event: {
    id: "abc",
    name: "L'événement",
    routes: {
      details: "#event_details",
    },
  },
  supportGroup: {
    name: "Le Groupe",
    url: "/",
    routes: {
      manage: "#group__manage",
    },
  },
  individual: {
    firstName: "Foo Bar",
    email: "foo@bar.com",
  },
  routes: {
    newGroupHelp: "#newGroupHelp",
    groupTransfer: "#groupTransfer",
    groupTransferHelp: "#groupTransferHelp",
  },
  meta: {
    membershipLimit: 30,
    membershipCount: 30,
    membershipLimitNotificationStep: 0,
  },
};
export const GroupInvitation = Template.bind({});
GroupInvitation.args = {
  ...WaitingPayment.args,
  type: "group-invitation",
};
export const NewMember = Template.bind({});
NewMember.args = {
  ...WaitingPayment.args,
  type: "new-member",
};
export const WaitingLocationGroup = Template.bind({});
WaitingLocationGroup.args = {
  ...WaitingPayment.args,
  type: "waiting-location-group",
};
export const GroupCoorganizationInvite = Template.bind({});
GroupCoorganizationInvite.args = {
  ...WaitingPayment.args,
  type: "group-coorganization-invite",
};
export const WaitingLocationEvent = Template.bind({});
WaitingLocationEvent.args = {
  ...WaitingPayment.args,
  type: "waiting-location-event",
};
export const GroupCreationConfirmation = Template.bind({});
GroupCreationConfirmation.args = {
  ...WaitingPayment.args,
  type: "group-creation-confirmation",
};
export const GroupMembershipLimitReminder = Template.bind({});
GroupMembershipLimitReminder.args = {
  ...WaitingPayment.args,
  type: "group-membership-limit-reminder",
};
