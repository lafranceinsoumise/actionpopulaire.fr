import React from "react";

import EventRequiredDocuments from "./EventRequiredDocuments";

import events from "@agir/front/mockData/events.json";
import subtypes from "@agir/front/mockData/eventSubtypes";
import { EVENT_PROJECT_STATUS, EVENT_DOCUMENT_TYPES } from "./config";

export default {
  component: EventRequiredDocuments,
  title: "Event Required Documents/EventRequiredDocuments",
  argTypes: {
    status: {
      options: Object.keys(EVENT_PROJECT_STATUS),
      control: { type: "radio" },
    },
  },
};

const Template = (args) => (
  <EventRequiredDocuments
    {...args}
    status={EVENT_PROJECT_STATUS[args.status]}
  />
);

export const Default = Template.bind({});
Default.args = {
  event: {
    id: events[0].id,
    name: events[0].name,
    endTime: events[0].endTime,
    subtype: events[0].subtype,
  },
  subtypes,
  projectId: "abc",
  status: "pending",
  requiredDocumentTypes: Object.keys(EVENT_DOCUMENT_TYPES).slice(0, 2),
  documents: [
    {
      id: "doc",
      name: "Attestation de concours en nature",
      link: "#doc",
    },
  ],
  limitDate: "2022-01-01 00:00:00",
  isLoading: false,
};
