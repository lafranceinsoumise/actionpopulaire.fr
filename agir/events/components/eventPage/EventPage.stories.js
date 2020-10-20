import React from "react";
import { DateTime } from "luxon";

import EventPage from "./EventPage";
import { TestGlobalContextProvider } from "@agir/front/genericComponents/GobalContext";
import { Default as DescriptionStory } from "./Description.stories";
import { Default as EventInfoStory } from "./EventInfo.stories";
import { Default as GroupCardStory } from "./GroupCard.stories";

export default {
  component: EventPage,
  title: "Events/EventPage",
  decorators: [
    (story, { args }) => (
      <TestGlobalContextProvider
        value={{ user: args.logged ? {} : null, routes: testGlobalRoutes }}
      >
        {story()}
      </TestGlobalContextProvider>
    ),
  ],
};

const testAppRoutes = [
  "page",
  "join",
  "cancel",
  "manage",
  "calendarExport",
  "googleExport",
  "outlookExport",
].reduce((o, p) => ((o[p] = `#${p}`), o), {});
testAppRoutes.map =
  "https://agir.lafranceinsoumise.fr/carte/evenements/00673c7f-1183-4504-85d4-bbf4c190e71f/";

const testGlobalRoutes = { logIn: "#login", signIn: "#signin" };

const defaultStartTime = DateTime.local().plus({ days: 2 });
const defaultEndTime = defaultStartTime.plus({ hours: 2 });

const Template = ({ locationName, locationAddress, ...args }) => (
  <EventPage
    {...args}
    location={{ name: locationName, address: locationAddress }}
  />
);

export const Default = Template.bind({});
Default.args = {
  id: "12343432423",
  name: "Super événement",
  ...DescriptionStory.args,
  ...EventInfoStory.args,
  group: { ...GroupCardStory.args },
  startTime: defaultStartTime.toISO(),
  endTime: defaultEndTime.toISO(),
  options: { price: null },
  routes: testAppRoutes,
  locationName: "Place de la République",
  locationAddress: "Place de la République\n75011 Paris",
};
