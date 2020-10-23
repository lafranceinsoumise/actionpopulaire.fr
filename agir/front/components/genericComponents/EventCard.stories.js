import React from "react";

import EventCard from "./EventCard";
import { DateTime, Interval } from "luxon";
import { Container, GrayBackground } from "@agir/front/genericComponents/grid";

export default {
  component: EventCard,
  title: "Generic/EventCard",
};

const defaultStartTime = DateTime.local().plus({ days: 2 });
const defaultEndTime = defaultStartTime.plus({ hours: 2 });

const Template = (args) => {
  return (
    <GrayBackground style={{ padding: "40px" }}>
      <Container>
        <EventCard {...args} />
      </Container>
    </GrayBackground>
  );
};

export const Default = Template.bind({});
Default.args = {};

Default.args = {
  id: "12343432423",
  name: "Super événement",
  rsvp: "CO",
  participantCount: 6,
  schedule: Interval.fromDateTimes(
    DateTime.fromISO(defaultStartTime.toISO()).setLocale("fr"),
    DateTime.fromISO(defaultEndTime.toISO()).setLocale("fr")
  ),
  illustration:
    "https://i.picsum.photos/id/523/1920/1080.jpg?hmac=sy_3fHrsxYu8cmYYWmQ2yWzPMfGNI42qloxWKF97ISk",
  location: {
    name: "Place de la République",
    address: "Place de la République\n75011 Paris",
    shortAddress: "Place de la République, 75011, Paris",
  },
  routes: {
    join: "#join",
    cancel: "#cancel",
    compteRendu: "#compteRendu",
  },
};
