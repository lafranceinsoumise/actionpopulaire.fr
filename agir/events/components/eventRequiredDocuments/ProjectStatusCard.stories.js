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
    <ProjectStatusCard {...args} status={EVENT_PROJECT_STATUS[args.status]} />
  </div>
);

export const Pending = Template.bind({});
Pending.args = {
  status: "pending",
};

export const Archived = Template.bind({});
Archived.args = {
  status: "archived",
};
