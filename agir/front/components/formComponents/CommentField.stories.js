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

const Template = (args) => {
  const [messages, setMessages] = React.useState([args.initialMessage]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [errors, setErrors] = React.useState(args.errors);

  const scrollerRef = React.useRef();
  const handleSend = React.useCallback(async (text) => {
    await new Promise((resolve) => {
      setIsLoading(true);
      setErrors(null);
      setTimeout(() => {
        setIsLoading(false);
        if (args.errors) {
          setErrors(args.errors);
        } else {
          setMessages((state) => [
            ...state,
            {
              id: state.length,
              author: user,
              text,
              created: new Date().toUTCString(),
            },
          ]);
        }
        resolve();
      }, 3000);
    });
  }, []);

  return (
    <div
      style={{
        background: "white",
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
          errors={errors}
        />
      </div>
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  initialMessage: {
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
};

export const WithErrors = Template.bind({});
WithErrors.args = {
  ...Default.args,
  errors: {
    text: "Beaucoup trop long comme texte !",
    attachment: {
      name: "Nope !",
      file: [
        "L'extension de fichier « webm » n’est pas autorisée. Les extensions autorisées sont :  pdf, doc, docx, odt, xls, xlsx, ods, ppt, pptx, odp, png, jpeg, jpg, gif.",
        "Le fichier joint est beaucoup trop grand",
      ],
    },
  },
};

export const ButtonOnly = () => {
  return <CommentButton user={user} onClick={() => {}} />;
};
