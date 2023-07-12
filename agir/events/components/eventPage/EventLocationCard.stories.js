import React from "react";

import EventLocationCard from "./EventLocationCard";
import { DateTime } from "luxon";
import {
  decorateArgs,
  reorganize,
  scheduleFromStartTimeAndDuration,
} from "@agir/lib/utils/storyUtils";

export default {
  component: EventLocationCard,
  title: "Events/EventPage/EventLocation",
  argTypes: {
    startTime: {
      type: "string",
      control: { type: "date" },
    },
    location: { table: { disable: true } },
    routes: { table: { disable: true } },
    schedule: { table: { disable: true } },
  },
  decorators: [
    (Story, { args: { maxWidth } }) => (
      <div style={{ maxWidth, margin: "1rem" }}>
        <Story />
      </div>
    ),
  ],
};

const Template = decorateArgs(
  scheduleFromStartTimeAndDuration(),
  reorganize({
    location: { name: "locationName", address: "locationAddress" },
  }),
  EventLocationCard,
);

export const Default = Template.bind({});
Default.args = {
  timezone: "Europe/Paris",
  startTime: DateTime.local().plus({ days: 1 }).toMillis(),
  duration: 2,
  locationName: "Place de la République",
  locationAddress: "Place de la République\n75011 Paris",
  routes: {
    map: "https://agir.lafranceinsoumise.fr/carte/evenements/00673c7f-1183-4504-85d4-bbf4c190e71f/",
    googleCalendar: "#google",
    outlookCalendar: "#outlook",
    exportCalendar: "#export",
  },
  maxWidth: "500px",
};
