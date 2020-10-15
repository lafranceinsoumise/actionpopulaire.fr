import React from "react";

import EventLocation from "./EventLocation";
import { DateTime } from "luxon";

export default {
  component: EventLocation,
  title: "Events/EventLocation",
  argTypes: {
    date: {
      type: "string",
      control: { type: "date" },
    },
    location: { control: { disable: true } },
    routes: { control: { disable: true } },
  },
  decorators: [
    (Story, { args: { maxWidth, date } }) => (
      <div style={{ maxWidth }}>
        <Story />
      </div>
    ),
  ],
};

const Template = ({ date, locationName, locationAddress, ...args }) => {
  date = DateTime.fromMillis(+date, { zone: "Europe/Paris" }).setLocale("fr");

  return (
    <EventLocation
      {...args}
      date={date}
      location={{
        name: locationName,
        address: locationAddress,
      }}
    />
  );
};

export const Default = Template.bind({});
Default.args = {
  date: DateTime.local().plus({ days: 1 }),
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
