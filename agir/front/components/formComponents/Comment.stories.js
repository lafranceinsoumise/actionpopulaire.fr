import React from "react";

import Comment from "./Comment";

export default {
  component: Comment,
  title: "Form/Comment",
  argTypes: {
    onEdit: { action: "Edit" },
    onDelete: { action: "Delete" },
    onReport: { action: "Flag" },
  },
};

const author = {
  displayName: "Bill Murray",
  image: "https://loremflickr.com/200/200",
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
          <Comment
            {...args}
            onEdit={onEdit}
            onDelete={onDelete}
            onReport={onReport}
            isAuthor
          />
        ) : (
          <Comment {...args} />
        )}
      </div>
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  comment: {
    author,
    text: "Bonjour !\n\nBonjour !\nBonjour !",
    created: new Date().toUTCString(),
  },
  hasActions: false,
};

export const WithActions = Template.bind({});
WithActions.args = {
  comment: {
    author,
    text: "Bonjour !",
    created: new Date().toUTCString(),
  },
  hasActions: true,
};
