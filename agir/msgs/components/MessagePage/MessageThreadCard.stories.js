import React from "react";

import messages from "@agir/front/mockData/messages";

import MessageThreadCard from "./MessageThreadCard";

export default {
  component: MessageThreadCard,
  title: "Messages/MessagePage/MessageThreadCard",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => {
  return (
    <div style={{ maxWidth: 400 }}>
      <MessageThreadCard {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  message: messages[0],
  isSelected: false,
};

export const Selected = Template.bind({});
Selected.args = {
  ...Default.args,
  isSelected: true,
};

export const WithUnreadComments = Template.bind({});
WithUnreadComments.args = {
  ...Default.args,
  message: {
    ...Default.args.message,
    unreadCommentCount: 10,
  },
};
