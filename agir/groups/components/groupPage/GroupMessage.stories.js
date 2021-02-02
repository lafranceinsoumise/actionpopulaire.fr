import React from "react";

import GroupMessage from "./GroupMessage";

import events from "@agir/groups/groupPage/events.json";
import messages from "@agir/groups/groupPage/messages.json";

export default {
  component: GroupMessage,
  title: "Group/GroupMessage",
  argTypes: {
    createMessage: { action: "createMessage" },
    updateMessage: { action: "updateMessage" },
    createComment: { action: "createComment" },
    reportMessage: { action: "reportMessage" },
    deleteMessage: { action: "deleteMessage" },
  },
};

const args = {
  user: {
    id: "Bill",
    displayName: "Bill Murray",
    avatar: "https://www.fillmurray.com/200/200",
  },
  messages,
  events,
  messageURLBase: "#message__:id",
};

export const Default = () => {
  const [isLoading, setIsLoading] = React.useState(true);
  const [comments, setComments] = React.useState();
  const [message, setMessage] = React.useState();

  React.useEffect(() => {
    setTimeout(() => {
      setIsLoading(false);
      setComments(args.messages[0].comments);
      setMessage(args.messages[0]);
    }, 2000);
  }, []);

  const msg = React.useMemo(() => (message ? { ...message, comments } : null), [
    message,
    comments,
  ]);

  const saveMessage = React.useCallback((message, relatedMessage) => {
    if (relatedMessage) {
      const msg = {
        content: message,
        id: message.id || String(Date.now()),
        created: new Date().toUTCString(),
        author: args.user,
      };
      setComments((state) => [...state, msg]);
    } else {
      const msg = {
        ...message,
        linkedEvent: message.linkedEvent.id ? message.linkedEvent : null,
      };
      setMessage(msg);
    }
  }, []);

  const deleteMessage = React.useCallback((message) => {
    setComments((state) =>
      state.filter((comment) => comment.id !== message.id)
    );
  }, []);

  return (
    <div
      style={{
        maxWidth: 640,
        margin: "0 auto",
      }}
    >
      <GroupMessage
        {...args}
        isLoading={isLoading}
        message={msg}
        createMessage={saveMessage}
        updateMessage={saveMessage}
        deleteMessage={deleteMessage}
        createComment={saveMessage}
      />
    </div>
  );
};
