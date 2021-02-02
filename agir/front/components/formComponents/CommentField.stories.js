import React from "react";

import CommentField, { CommentButton } from "./CommentField";
import Comment from "./Comment";

export default {
  component: CommentField,
  title: "Form/CommentField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
};

const user = {
  fullName: "Bill Murray",
  avatar: "https://www.fillmurray.com/200/200",
};

export const Default = () => {
  const [messages, setMessages] = React.useState(["Bonjour."]);
  const [isLoading, setIsLoading] = React.useState(false);
  const handleSend = React.useCallback(async (message) => {
    await new Promise((resolve) => {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        setMessages((state) => [...state, message.trim()]);
        resolve();
      }, 3000);
    });
  }, []);

  return (
    <div
      style={{
        background: "lightgrey",
        minHeight: "100vh",
        padding: "16px",
      }}
    >
      {messages.map((message) => (
        <p
          style={{
            background: "white",
            borderRadius: "8px",
            maxWidth: "480px",
            padding: "0.875rem",
            margin: "8px auto",
            fontSize: "14px",
          }}
          key={message}
        >
          <strong>{user.fullName}</strong>
          <br />
          {message}
          <br />
          <small>
            <code>{JSON.stringify(message)}</code>
          </small>
        </p>
      ))}
      <div
        style={{
          boxSizing: "border-box",
          padding: "0",
          maxWidth: "480px",
          margin: "0 auto",
        }}
      >
        <CommentField
          key={messages.length}
          isLoading={isLoading}
          onSend={handleSend}
          id={`comment${messages.length}`}
          user={user}
        />
      </div>
    </div>
  );
};

export const WithComments = () => {
  const [messages, setMessages] = React.useState([
    {
      id: 0,
      content: "Bonjour !",
      author: {
        fullName: "Quelqu'un",
        avatar: `https://avatars.dicebear.com/api/human/${String(
          Math.random()
        ).replace(".", "")}.svg?background=%23ffffff`,
      },
      created: new Date().toUTCString(),
    },
  ]);
  const [isLoading, setIsLoading] = React.useState(false);
  const handleSend = React.useCallback(async (content) => {
    await new Promise((resolve) => {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        setMessages((state) => [
          ...state,
          {
            id: state.length,
            author: user,
            content,
            created: new Date().toUTCString(),
          },
        ]);
        resolve();
      }, 3000);
    });
  }, []);

  return (
    <div
      style={{
        background: "lightgrey",
        minHeight: "100vh",
        padding: "16px",
      }}
    >
      {messages.map((message) => (
        <div
          style={{
            maxWidth: "480px",
            margin: "8px auto",
          }}
          key={message.id}
        >
          <Comment message={message} />
        </div>
      ))}
      <div
        style={{
          boxSizing: "border-box",
          padding: "0",
          maxWidth: "480px",
          margin: "0 auto",
        }}
      >
        <CommentField
          key={messages.length}
          isLoading={isLoading}
          onSend={handleSend}
          id={`comment${messages.length}`}
          user={user}
        />
      </div>
    </div>
  );
};

export const ButtonOnly = () => {
  return <CommentButton user={user} onClick={() => {}} />;
};
