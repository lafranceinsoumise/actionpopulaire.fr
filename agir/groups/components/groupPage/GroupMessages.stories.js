import React from "react";
import _sortBy from "lodash/sortBy";

import GroupMessages from "./GroupMessages";

import events from "@agir/groups/groupPage/events.json";
import messages from "@agir/groups/groupPage/messages.json";

export default {
  component: GroupMessages,
  title: "Group/GroupMessages",
  argTypes: {
    createMessage: { action: "createMessage" },
    updateMessage: { action: "updateMessage" },
    createComment: { action: "createComment" },
    reportMessage: { action: "reportMessage" },
    deleteMessage: { action: "deleteMessage" },
    reportComment: { action: "reportComment" },
    deleteComment: { action: "deleteComment" },
  },
};

const Template = (args) => {
  const [hasLimit, setHasLimit] = React.useState(args.messages.length > 0);
  const [isLoading, setIsLoading] = React.useState(true);
  const [comments, setComments] = React.useState();
  const [messages, setMessages] = React.useState();

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
      const messages = Array.isArray(args.messages) ? args.messages : [];
      setComments(
        messages.reduce(
          (obj, message) => ({
            ...obj,
            [message.id]: message.comments,
          }),
          {}
        )
      );
      setMessages(
        messages.reduce(
          (obj, message) => ({
            ...obj,
            [message.id]: message,
          }),
          {}
        )
      );
    }, 2000);
  }, [args.messages]);

  const msgs = React.useMemo(
    () =>
      messages
        ? _sortBy(
            Object.values(messages)
              .filter(Boolean)
              .map((message) => ({
                ...message,
                comments: (comments && comments[message.id]) || [],
              })),
            ["created"]
          )
            .reverse()
            .slice(0, hasLimit ? 1 : undefined)
        : null,
    [hasLimit, messages, comments]
  );

  const saveMessage = React.useCallback(
    (message, relatedMessage) => {
      mockAction(() => {
        if (relatedMessage) {
          const msg = {
            content: message,
            id: message.id || Date.now(),
            created: new Date().toUTCString(),
            author: args.user,
          };
          setComments((state) => ({
            ...state,
            [relatedMessage.id]: [...(state[relatedMessage.id] || []), msg],
          }));
        } else {
          const msg = {
            ...message,
            id: message.id || Date.now(),
            created: new Date().toUTCString(),
            author: args.user,
            linkedEvent: message.linkedEvent.id ? message.linkedEvent : null,
          };
          setMessages((state) => ({
            ...state,
            [msg.id]: msg,
          }));
        }
      });
    },
    [args.user, mockAction]
  );

  const deleteMessage = React.useCallback(
    (message) => {
      mockAction(() => {
        if (messages[message.id]) {
          setMessages((state) => ({
            ...state,
            [message.id]: null,
          }));
          setComments((state) => ({
            ...state,
            [message.id]: [],
          }));
        }
      });
    },
    [mockAction, messages]
  );

  const reportMessage = React.useCallback(() => {
    mockAction(() => {});
  }, [mockAction]);

  const reportComment = React.useCallback(() => {
    mockAction(() => {});
  }, [mockAction]);

  const deleteComment = React.useCallback(() => {
    mockAction(() => {});
  }, [mockAction]);

  const loadMoreMessages = React.useCallback(() => {
    mockAction(() => setHasLimit(false));
  }, [mockAction]);

  return (
    <div
      style={{
        maxWidth: 640,
        margin: "0 auto",
      }}
    >
      <GroupMessages
        {...args}
        isLoading={isLoading}
        messages={msgs}
        createMessage={args.createMessage && saveMessage}
        updateMessage={args.updateMessage && saveMessage}
        deleteMessage={args.deleteMessage && deleteMessage}
        reportMessage={args.reportMessage && reportMessage}
        createComment={args.createComment && saveMessage}
        deleteComment={args.deleteComment && deleteComment}
        reportComment={args.reportComment && reportComment}
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
    avatar: "https://www.fillmurray.com/200/200",
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

export const Empty = Template.bind({});
Empty.args = {
  ...Default.args,
  messages: [],
};

export const ReadOnly = Template.bind({});
ReadOnly.args = {
  ...Default.args,
  createMessage: undefined,
  updateMessage: undefined,
  deleteMessage: undefined,
  reportMessage: undefined,
  createComment: undefined,
  deleteComment: undefined,
  reportComment: undefined,
};
