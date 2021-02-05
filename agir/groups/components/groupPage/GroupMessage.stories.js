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

const Template = (args) => {
  const [isLoading, setIsLoading] = React.useState(true);
  const [comments, setComments] = React.useState();
  const [message, setMessage] = React.useState();

  const mockAction = React.useCallback(async (action) => {
    setIsLoading(true);
    await new Promise((resolve) => {
      setTimeout(() => {
        action();
        setIsLoading(false);
        resolve();
      }, 2000);
    });
  }, []);

  React.useEffect(() => {
    setTimeout(() => {
      setIsLoading(false);
      setComments(args.message.comments);
      setMessage(args.message);
    }, 2000);
  }, [args.message]);

  const msg = React.useMemo(() => (message ? { ...message, comments } : null), [
    message,
    comments,
  ]);

  const saveMessage = React.useCallback(
    (message, relatedMessage) => {
      mockAction(() => {
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
      });
    },
    [mockAction, args.user]
  );

  const deleteMessage = React.useCallback(
    (message) => {
      mockAction(() => {
        setComments((state) =>
          state.filter((comment) => comment.id !== message.id)
        );
      });
    },
    [mockAction]
  );

  const reportMessage = React.useCallback(() => {
    mockAction(() => {});
  }, [mockAction]);

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
        createMessage={args.createMessage && saveMessage}
        updateMessage={args.updateMessage && saveMessage}
        deleteMessage={args.deleteMessage && deleteMessage}
        reportMessage={args.reportMessage && reportMessage}
        createComment={args.createComment && saveMessage}
      />
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

export const Empty = Template.bind({});
Empty.args = {
  ...Default.args,
  message: null,
};

export const ReadOnly = Template.bind({});
ReadOnly.args = {
  ...Default.args,
  createMessage: undefined,
  updateMessage: undefined,
  deleteMessage: undefined,
  reportMessage: undefined,
  createComment: undefined,
};
