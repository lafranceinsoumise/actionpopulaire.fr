import _sortBy from "lodash/sortBy";
import React from "react";

import mockMessages from "@agir/front/mockData/messages";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import MessageThreadList from "./MessageThreadList";

export default {
  component: MessageThreadList,
  title: "Messages/MessagePage/MessageThreadList",
  argTypes: {
    onEdit: { action: "onEdit" },
    onComment: { action: "onComment" },
    onReport: { action: "onReport" },
    onDelete: { action: "onDelete" },
    onReportComment: { action: "onReportComment" },
    onDeleteComment: { action: "onDeleteComment" },
  },
};

const Template = (args) => {
  const [selectedId, setSelectedId] = React.useState(null);

  const selected = React.useMemo(
    () => (selectedId ? messages.find(({ id }) => id === selectedId) : null),
    [selectedId]
  );

  return (
    <TestGlobalContextProvider>
      <div
        style={{
          width: "100%",
          height: "100vh",
          padding: "0",
        }}
      >
        <MessageThreadList
          {...args}
          selectedMessage={selected}
          onSelect={setSelectedId}
        />
      </div>
    </TestGlobalContextProvider>
  );
};

const messages = _sortBy(
  mockMessages.map((message) => ({
    ...message,
    commentCount: undefined,
    unreadCommentCount: message?.comments?.length
      ? Math.round(Math.random() * 10)
      : 0,
  })),
  ["unreadCommentCount"]
).reverse();

export const Default = Template.bind({});
Default.args = {
  messages,
  user: messages[0].author,
  notificationSettingLink: "#parametres",
};

export const WithNewMessageButton = Template.bind({});
WithNewMessageButton.args = Default.args;
WithNewMessageButton.argTypes = {
  writeNewMessage: { action: "writeNewMessage" },
};
