import React from "react";

import events from "@agir/front/mockData/events";
import MissingDocumentList from "./MissingDocumentList";

export default {
  component: MissingDocumentList,
  title: "Event Required Documents/Missing Documents/MissingDocumentList",
};

const Template = (args) => (
  <div style={{ maxWidth: 660, width: "100%", margin: "32px auto" }}>
    <MissingDocumentList projects={args.projects.slice(0, args.howMany)} />
  </div>
);

export const Default = Template.bind({});
Default.args = {
  howMany: 3,
  projects: events.map((event, i) => ({
    event: {
      id: event.id,
      name: event.name,
      endTime: event.endTime,
    },
    projectId: i,
    missingDocumentCount: 2,
    limitDate: "2022-01-01 00:00:00",
  })),
};
