import React from "react";

import EventPage from "./EventPage";
import { Default as DescriptionStory } from "./Description.stories";
import { Default as EventHeaderStory } from "./EventHeader.stories";
import { DateTime } from "luxon";
import { TestConfigProvider } from "@agir/front/genericComponents/Config";

const testGlobalRoutes = { logIn: "#login", signIn: "#signin" };

const testAppRoutes = [
  "page",
  "map",
  "join",
  "cancel",
  "manage",
  "calendarExport",
  "googleExport",
  "outlookExport",
].reduce((o, p) => (o[p] = `#${p}`), {});

export default {
  component: EventPage,
  title: "Events/EventPage",
  decorators: [
    (story, { args }) => (
      <TestConfigProvider
        value={{ user: args.logged ? {} : null, routes: testGlobalRoutes }}
      >
        {story()}
      </TestConfigProvider>
    ),
  ],
};

const Template = (args) => <EventPage {...args} />;

const defaultStartTime = DateTime.local().plus({ days: 2 });
const defaultEndTime = defaultStartTime.plus({ hours: 2 });

export const Default = Template.bind({});
Default.args = {
  id: "12343432423",
  ...EventHeaderStory.args,
  ...DescriptionStory.args,
  startTime: defaultStartTime.toISO(),
  endTime: defaultEndTime.toISO(),
  locationName: "Place de la République",
  locationAddress: "Place de la République\n75011 Paris",
  routes: testAppRoutes,
  logged: true,
};
