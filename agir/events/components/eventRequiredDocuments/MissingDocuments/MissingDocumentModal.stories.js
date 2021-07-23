import React from "react";

import events from "@agir/front/mockData/events";
import { MissingDocumentModal } from "./MissingDocumentModal";

export default {
  component: MissingDocumentModal,
  title: "Event Required Documents/Missing Documents/MissingDocumentModal",
};

const Template = (args) => <MissingDocumentModal {...args} />;

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  projects: events.slice(0, 3).map((event, i) => ({
    event: {
      id: event.id,
      name: event.name,
      endTime: event.endTime,
    },
    projectId: i,
    missingDocumentCount: 2,
    limitDate: "2022-01-01 00:00:00",
  })),
  isBlocked: true,
};

export const Empty = Template.bind({});
Empty.args = {
  ...Default.args,
  projects: [],
};
