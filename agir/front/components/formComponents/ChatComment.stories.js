import React from "react";

import ChatComment from "./ChatComment";

export default {
  component: ChatComment,
  title: "Form/ChatComment",
  argTypes: {
    onEdit: { action: "Edit" },
    onDelete: { action: "Delete" },
    onReport: { action: "Flag" },
  },
};

const author = {
  fullName: "Bill Murray",
  avatar: "https://www.fillmurray.com/200/200",
};
const Template = ({ hasActions, onEdit, onDelete, onReport, ...args }) => {
  return (
    <div
      style={{
        background: "lightgrey",
        minHeight: "100vh",
        padding: "16px",
      }}
    >
      <div
        style={{
          boxSizing: "border-box",
          padding: "0",
          maxWidth: "480px",
          margin: "0 auto",
        }}
      >
        {hasActions ? (
          <ChatComment
            {...args}
            onEdit={onEdit}
            onDelete={onDelete}
            onReport={onReport}
          />
        ) : (
          <ChatComment {...args} />
        )}
      </div>
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  author,
  message: "Bonjour !",
  date: new Date().toUTCString(),
  hasActions: false,
};

export const WithActions = Template.bind({});
WithActions.args = {
  author,
  message: "Bonjour !",
  date: new Date().toUTCString(),
  hasActions: true,
};
