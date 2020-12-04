import React from "react";
import { FeedbackButton } from "./FeedbackButton";

export default {
  component: FeedbackButton,
  title: "Layout/FeedbackButton",
};

const Template = (args) => <FeedbackButton {...args} />;

export const Default = Template.bind({});
Default.args = {
  isActive: true,
  shouldPushTooltip: true,
  href: "#feedback-form",
};
