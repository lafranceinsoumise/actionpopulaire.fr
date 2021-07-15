import React from "react";

import NoRequiredDocumentCard from "./NoRequiredDocumentCard";

export default {
  component: NoRequiredDocumentCard,
  title: "Event Required Documents/NoRequiredDocumentCard",
  parameters: {
    layout: "centered",
  },
};

const Template = () => (
  <div style={{ maxWidth: 372, width: "100%" }}>
    <NoRequiredDocumentCard />
  </div>
);

export const Default = Template.bind({});
