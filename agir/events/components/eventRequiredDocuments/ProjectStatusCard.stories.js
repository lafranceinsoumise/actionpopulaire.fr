import React from "react";

import ProjectStatusCard from "./ProjectStatusCard";

import { EVENT_PROJECT_STATUS } from "./config";

export default {
  component: ProjectStatusCard,
  title: "Event Required Documents/ProjectStatusCard",
  parameters: {
    layout: "centered",
  },
  argTypes: {
    status: {
      options: Object.keys(EVENT_PROJECT_STATUS),
      control: { type: "radio" },
    },
  },
};

const Template = (args) => (
  <div style={{ maxWidth: 372, width: "100%" }}>
    <ProjectStatusCard {...args} />
  </div>
);

export const WithoutRequiredDocs = Template.bind({});
WithoutRequiredDocs.args = {
  status: "DFI",
  hasRequiredDocuments: false,
  hasDismissedAllDocuments: false,
  hasMissingDocuments: false,
};

export const AllDocumentsDismissed = Template.bind({});
AllDocumentsDismissed.args = {
  status: "DFI",
  hasRequiredDocuments: true,
  hasDismissedAllDocuments: true,
  hasMissingDocuments: false,
};

export const Pending = Template.bind({});
Pending.args = {
  status: "DFI",
  hasRequiredDocuments: true,
  hasDismissedAllDocuments: false,
  hasMissingDocuments: false,
};

export const Archived = Template.bind({});
Archived.args = {
  ...Pending.args,
  status: "CLO",
};

export const Refused = Template.bind({});
Refused.args = {
  ...Pending.args,
  status: "REF",
};
