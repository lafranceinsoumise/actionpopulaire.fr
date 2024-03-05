import React from "react";

import CommentField, { CommentButton } from "./CommentField";
import Comment from "./Comment";
import MessageAttachment from "./MessageAttachment";

export default {
  component: CommentField,
  title: "Form/CommentField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
};

const user = {
  displayName: "Bill Murray",
  image: "https://loremflickr.com/200/200",
};

export const Default = () => {
  const [messages, setMessages] = React.useState([["Bonjour."]]);
  const [isLoading, setIsLoading] = React.useState(false);
  const scrollerRef = React.useRef();
  const handleSend = React.useCallback(async (message, attachment) => {
    await new Promise((resolve) => {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        setMessages((state) => [...state, [message.trim(), attachment]]);
        resolve();
      }, 3000);
    });
  }, []);

  return (
    <div
      ref={scrollerRef}
      style={{
        background: "lightgrey",
        minHeight: "100vh",
        padding: "16px",
        maxWidth: "100%",
        overflowX: "hidden",
      }}
    >
      {messages.map(([message, attachment]) => (
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
          <strong>{user.displayName}</strong>
          <br />
          {message}
          <br />
          <br />
          <MessageAttachment file={attachment?.file} name={attachment?.name} />
        </p>
      ))}
      <div
        style={{
          maxWidth: "480px",
          margin: "2rem auto",
        }}
      >
        <CommentField
          key={messages.length}
          isLoading={isLoading}
          onSend={handleSend}
          id={`comment${messages.length}`}
          user={user}
          scrollerRef={scrollerRef}
        />
      </div>
    </div>
  );
};

export const WithComments = () => {
  const [messages, setMessages] = React.useState([
    {
      id: 0,
      text: "Bonjour !",
      author: {
        displayName: "Quelqu'un",
        image: `https://images.dicebear.com/api/human/${String(
          Math.random(),
        ).replace(".", "")}.svg?background=%23ffffff`,
      },
      created: new Date().toUTCString(),
    },
  ]);
  const [isLoading, setIsLoading] = React.useState(false);
  const scrollerRef = React.useRef();
  const handleSend = React.useCallback(async (text) => {
    await new Promise((resolve) => {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        setMessages((state) => [
          ...state,
          {
            id: state.length,
            author: user,
            text,
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
      ref={scrollerRef}
    >
      {messages.map((message) => (
        <div
          style={{
            maxWidth: "480px",
            margin: "8px auto",
          }}
          key={message.id}
        >
          <Comment comment={message} />
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
          scrollerRef={scrollerRef}
        />
      </div>
    </div>
  );
};

export const ButtonOnly = () => {
  return <CommentButton user={user} onClick={() => {}} />;
};
