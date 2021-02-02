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
  const [hasLimit, setHasLimit] = React.useState(true);
  const [isLoading, setIsLoading] = React.useState(true);
  const [comments, setComments] = React.useState();
  const [messages, setMessages] = React.useState();
  React.useEffect(() => {
    setTimeout(() => {
      setIsLoading(false);
      setComments(
        args.messages.reduce(
          (obj, message) => ({
            ...obj,
            [message.id]: message.comments,
          }),
          {}
        )
      );
      setMessages(
        args.messages.reduce(
          (obj, message) => ({
            ...obj,
            [message.id]: message,
          }),
          {}
        )
      );
    }, 2000);
    //eslint-disable-next-line
  }, []);

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

  const saveMessage = React.useCallback((message, relatedMessage) => {
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
  }, []);

  const deleteMessage = React.useCallback(
    (message, relatedMessage) => {
      if (relatedMessage && comments[relatedMessage.id]) {
        setComments((state) => ({
          ...state,
          [relatedMessage.id]: (state[relatedMessage.id] || []).filter(
            (comment) => comment.id !== message.id
          ),
        }));
      }
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
    },
    [messages, comments]
  );

  const loadMoreMessages = React.useCallback(() => {
    setHasLimit(false);
  }, []);

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
        createMessage={saveMessage}
        updateMessage={saveMessage}
        deleteMessage={deleteMessage}
        createComment={saveMessage}
        loadMoreMessages={hasLimit ? loadMoreMessages : undefined}
      />
    </div>
  );
};

export const Empty = () => {
  const [isLoading, setIsLoading] = React.useState(true);
  const [comments, setComments] = React.useState();
  const [messages, setMessages] = React.useState();

  React.useEffect(() => {
    setTimeout(() => {
      setIsLoading(false);
      setComments({});
      setMessages({});
    }, 2000);
    //eslint-disable-next-line
  }, []);

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
          ).reverse()
        : null,
    [messages, comments]
  );

  const saveMessage = React.useCallback((message, relatedMessage) => {
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
  }, []);

  const deleteMessage = React.useCallback(
    (message, relatedMessage) => {
      if (relatedMessage && comments[relatedMessage.id]) {
        setComments((state) => ({
          ...state,
          [relatedMessage.id]: (state[relatedMessage.id] || []).filter(
            (comment) => comment.id !== message.id
          ),
        }));
      }
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
    },
    [messages, comments]
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
        isLoading={isLoading}
        messages={msgs}
        createMessage={saveMessage}
        updateMessage={saveMessage}
        deleteMessage={deleteMessage}
        createComment={saveMessage}
      />
    </div>
  );
};
