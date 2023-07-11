import _sortBy from "lodash/sortBy";
import React from "react";

import mockMessages from "@agir/front/mockData/messages";

import MessageThreadMenu from "./MessageThreadMenu";

export default {
  component: MessageThreadMenu,
  title: "Messages/MessagePage/MessageThreadMenu",
};

const Template = (args) => {
  const [selectedId, setSelectedId] = React.useState(null);

  const selected = React.useMemo(
    () =>
      selectedId ? messages.find(({ id }) => id === selectedId) : messages[0],
    [selectedId],
  );

  return (
    <div
      style={{
        width: "100%",
        height: "100vh",
        padding: "1.5rem",
      }}
    >
      <MessageThreadMenu
        {...args}
        selectedMessage={selected}
        onSelect={setSelectedId}
      />
    </div>
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
  ["unreadCommentCount"],
).reverse();

export const Default = Template.bind({});
Default.args = {
  messages,
  notificationSettingLink: "#parametres",
};

export const WithNewMessageButton = Template.bind({});
WithNewMessageButton.args = Default.args;
WithNewMessageButton.argTypes = {
  writeNewMessage: { action: "writeNewMessage" },
};
