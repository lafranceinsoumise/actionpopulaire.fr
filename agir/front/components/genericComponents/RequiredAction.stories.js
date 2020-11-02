import React from "react";

import RequiredAction from "./RequiredAction";

export default {
  component: RequiredAction,
  title: "Generic/RequiredAction",
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
      <RequiredAction {...args} />
    </div>
  );
};

export const WaitingPayment = Template.bind({});
WaitingPayment.args = {
  type: "waiting-payment",
  id: String(Date.now()),
  event: {
    name: "L'événement",
    routes: {
      details: "/",
    },
  },
  supportGroup: {
    name: "Le Groupe",
    url: "/",
  },
  individual: {
    fullName: "Foo Bar",
    email: "foo@bar.com",
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
