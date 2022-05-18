import React from "react";

import RequiredDocumentCard from "./RequiredDocumentCard";

import { EVENT_DOCUMENT_TYPES } from "./config";

export default {
  component: RequiredDocumentCard,
  title: "Event Required Documents/RequiredDocumentCard",
  argTypes: {
    type: {
      options: Object.keys(EVENT_DOCUMENT_TYPES),
      control: { type: "radio" },
    },
  },
};

const Template = (args) => (
  <div style={{ minWidth: 372, maxWidth: "90%", margin: "24px auto" }}>
    <RequiredDocumentCard {...args} />
  </div>
);

export const Default = Template.bind({});
Default.args = {
  type: Object.keys(EVENT_DOCUMENT_TYPES)[0],
  embedded: false,
};

export const Optional = Template.bind({});
Optional.args = {
  ...Default.args,
  onDismiss: null,
};

export const Embedded = Template.bind({});
Embedded.args = {
  ...Default.args,
  embedded: true,
};

export const DownloadOnly = Template.bind({});
DownloadOnly.args = {
  ...Default.args,
  downloadOnly: true,
};
