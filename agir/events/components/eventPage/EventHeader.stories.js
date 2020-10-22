import React from "react";
import { DateTime, Duration, Interval } from "luxon";

import EventHeader from "./EventHeader";
import { TestGlobalContextProvider } from "@agir/front/genericComponents/GobalContext";

const routes = { logIn: "#login", signIn: "#signin" };

const defaultStartTime = DateTime.local().plus({ days: 2 });
const defaultEndTime = defaultStartTime.plus({ hours: 2 });

export default {
  component: EventHeader,
  title: "Events/EventHeader",
  decorators: [
    (story, { args }) => (
      <TestGlobalContextProvider
        value={{ user: args.logged ? {} : null, routes }}
      >
        <div style={{ margin: "1rem" }}>{story()}</div>
      </TestGlobalContextProvider>
    ),
  ],
  argTypes: {
    logged: {
      type: "boolean",
    },
    startTime: {
      type: "string",
      control: { type: "date" },
    },
    routes: {
      table: { disable: true },
    },
    options: {
      table: { disable: true },
    },
    rsvp: {
      table: { disable: true },
    },
    schedule: {
      table: { disable: true },
    },
  },
};

const Template = ({ startTime, duration, price, rsvped, ...args }) => {
  const schedule = Interval.after(
    DateTime.fromMillis(+startTime, {
      zone: "Europe/Paris",
      locale: "fr",
    }),
    Duration.fromObject({ hours: duration })
  );

  return (
    <EventHeader
      {...args}
      schedule={schedule}
      options={price !== "" ? { price } : {}}
      rsvp={rsvped ? { id: "prout" } : null}
    />
  );
};

export const Default = Template.bind({});
Default.args = {
  name: "Mon événement",
  startTime: defaultStartTime.toMillis(),
  duration: 2,
  logged: true,
  price: "",
  routes: {
    page: "#page",
    join: "#join",
    cancel: "#cancel",
  },
};
