import React from "react";

import EventCard from "./EventCard";
import { DateTime } from "luxon";
import { Container } from "@agir/front/genericComponents/grid";
import {
  decorateArgs,
  reorganize,
  scheduleFromStartTimeAndDuration,
} from "@agir/lib/utils/storyUtils";

export default {
  component: EventCard,
  title: "Generic/EventCard",
  argTypes: {
    startTime: {
      control: {
        type: "date",
      },
    },
  },
  decorators: [
    (story) => (
      <div style={{ maxWidth: 800, margin: "40px auto" }}>
        <Container>{story()}</Container>
      </div>
    ),
  ],
};

const defaultStartTime = DateTime.local().plus({ days: 2 });

const Template = decorateArgs(
  scheduleFromStartTimeAndDuration(),
  reorganize({
    location: {
      name: "locationName",
      address: "locationAddress",
      shortLocation: "shortLocation",
      coordinates: "locationCoordinates",
    },
  }),
  EventCard,
);

export const Default = Template.bind({});
Default.args = {};

Default.args = {
  id: "12343432423",
  name: "Super événement",
  rsvp: "CO",
  participantCount: 6,
  startTime: defaultStartTime.toMillis(),
  duration: 2,
  illustration: {
    thumbnail: "https://loremflickr.com/1920/1080",
  },
  locationName: "Place de la République",
  locationAddress: "Place de la République\n75011 Paris",
  shortLocation: "Place de la République, 75011, Paris",
  locationCoordinates: {
    coordinates: [5.03586, 43.83125],
  },
  routes: {
    join: "#join",
    cancel: "#cancel",
    details: "#details",
  },
  groups: [
    { id: "A", name: "Groupe d'action 1" },
    { id: "B", name: "Groupe d'action B" },
  ],
};

export const WithMap = Template.bind({});
WithMap.args = {
  ...Default.args,
  illustration: null,
};

export const WithoutImageAndMap = Template.bind({});
WithoutImageAndMap.args = {
  ...Default.args,
  illustration: null,
  locationCoordinates: null,
};
