import React from "react";

import EventCard from "./EventCard";
import { DateTime } from "luxon";
import { Container, GrayBackground } from "@agir/front/genericComponents/grid";
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
      <GrayBackground style={{ padding: "40px" }}>
        <Container>{story()}</Container>
      </GrayBackground>
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
      shortAddress: "shortAddress",
    },
  }),
  EventCard
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
  illustration:
    "https://i.picsum.photos/id/523/1920/1080.jpg?hmac=sy_3fHrsxYu8cmYYWmQ2yWzPMfGNI42qloxWKF97ISk",
  locationName: "Place de la République",
  locationAddress: "Place de la République\n75011 Paris",
  shortAddress: "Place de la République, 75011, Paris",
  routes: {
    join: "#join",
    cancel: "#cancel",
    compteRendu: "#compteRendu",
    details: "#details",
  },
};
