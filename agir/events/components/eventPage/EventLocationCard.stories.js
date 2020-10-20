import React from "react";

import EventLocationCard from "./EventLocationCard";
import { DateTime } from "luxon";

export default {
  component: EventLocationCard,
  title: "Events/EventLocation",
  argTypes: {
    startTime: {
      type: "string",
      control: { type: "date" },
    },
    location: { control: { disable: true } },
    routes: { control: { disable: true } },
  },
  decorators: [
    (Story, { args: { maxWidth, startTime } }) => (
      <div style={{ maxWidth }}>
        <Story />
      </div>
    ),
  ],
};

const Template = ({ startTime, locationName, locationAddress, ...args }) => {
  startTime = DateTime.fromMillis(+startTime, {
    zone: "Europe/Paris",
  }).setLocale("fr");

  return (
    <EventLocationCard
      {...args}
      startTime={startTime}
      location={{
        name: locationName,
        address: locationAddress,
      }}
    />
  );
};

export const Default = Template.bind({});
Default.args = {
  startTime: DateTime.local().plus({ days: 1 }),
  locationName: "Place de la République",
  locationAddress: "Place de la République\n75011 Paris",
  routes: {
    map:
      "https://agir.lafranceinsoumise.fr/carte/evenements/00673c7f-1183-4504-85d4-bbf4c190e71f/",
    googleCalendar: "#google",
    outlookCalendar: "#outlook",
    exportCalendar: "#export",
  },
  maxWidth: "500px",
};
