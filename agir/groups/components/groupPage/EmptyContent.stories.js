import React from "react";

import EmptyContent, {
  MemberEmptyEvents,
  ManagerEmptyEvents,
  EmptyReports,
  EmptyMessages,
} from "./EmptyContent";

export default {
  component: EmptyContent,
  title: "Group/EmptyContent",
};

const Template = (args) => {
  return <EmptyContent {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  icon: "calendar",
  children: "Ce groupe n’a pas encore créé d’événement.",
};

export const EventsForMember = () => <MemberEmptyEvents />;
export const EventsForManager = () => <ManagerEmptyEvents />;
export const Reports = () => <EmptyReports />;
export const Messages = () => <EmptyMessages onClickSendMessage={() => {}} />;
