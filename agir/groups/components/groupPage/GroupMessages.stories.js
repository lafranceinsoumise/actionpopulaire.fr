import React from "react";

import { GroupMessages } from "./GroupMessages";

import events from "@agir/front/mockData/events.json";
import messages from "@agir/front/mockData/messages.json";

export default {
  component: GroupMessages,
  title: "Group/GroupMessages",
  argTypes: {
    getMessageURL: { action: "getMessageURL" },
    onClick: { action: "onClick" },
    loadMoreEvents: { action: "loadMoreEvents" },
    loadMoreMessages: { action: "loadMoreMessages" },
    writeNewMessage: { action: "writeNewMessage" },
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
  const [hasLimit, setHasLimit] = React.useState(args.messages.length > 0);

  const loadMoreMessages = React.useCallback(() => {
    () => setHasLimit(false);
  }, []);

  const msgs = React.useMemo(
    () => (hasLimit ? args.messages.slice(0, 1) : args.messages),
    [args.messages, hasLimit]
  );

  return (
    <div
      style={{
        maxWidth: 640,
        margin: "0 auto",
      }}
    >
      <GroupMessages
        {...args}
        messages={msgs}
        loadMoreMessages={hasLimit ? loadMoreMessages : undefined}
      />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  user: {
    id: "Bill",
    displayName: "Bill Murray",
    image: "https://www.fillmurray.com/200/200",
  },
  messages,
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
  messages: [],
};

export const ReadOnly = Template.bind({});
ReadOnly.args = {
  ...Default.args,
  writeNewMessage: undefined,
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
