import React from "react";

import { GroupMessage } from "./GroupMessage";

import events from "@agir/groups/groupPage/events.json";
import messages from "@agir/groups/groupPage/messages.json";

export default {
  component: GroupMessage,
  title: "Group/GroupMessage",
  argTypes: {
    onClick: { action: "onClick" },
    editMessage: { action: "editMessage" },
    confirmReport: { action: "confirmReport" },
    confirmDelete: { action: "confirmDelete" },
    writeNewComment: { action: "writeNewComment" },
    confirmReportComment: { action: "confirmReportComment" },
    confirmDeleteComment: { action: "confirmDeleteComment" },
    dismissMessageAction: { action: "dismissMessageAction" },
    saveMessage: { action: "saveMessage" },
    onDelete: { action: "onDelete" },
    onReport: { action: "onReport" },
  },
};

const Template = (args) => {
  return (
    <div
      style={{
        maxWidth: 640,
        margin: "0 auto",
      }}
    >
      <GroupMessage {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  user: messages[0].author,
  message: messages[0],
  events,
  messageURLBase: "#message__:id",
};

export const Manager = Template.bind({});
Manager.args = {
  ...Default.args,
  isManager: true,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  isLoading: true,
};

export const Empty = Template.bind({});
Empty.args = {
  ...Default.args,
  message: null,
};

export const ReadOnly = Template.bind({});
ReadOnly.args = {
  ...Default.args,
  editMessage: undefined,
  confirmReport: undefined,
  confirmDelete: undefined,
  writeNewComment: undefined,
  confirmReportComment: undefined,
  confirmDeleteComment: undefined,
  dismissMessageAction: undefined,
  saveMessage: undefined,
  onDelete: undefined,
  onReport: undefined,
};
