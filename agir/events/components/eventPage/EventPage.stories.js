import React from "react";
import { DateTime } from "luxon";

import { EventPage } from "./EventPage";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import { Default as DescriptionStory } from "./EventDescription.stories";
import { Default as EventInfoStory } from "./EventInfoCard.stories";
import { Default as GroupCardStory } from "@agir/groups/groupComponents/GroupCard.stories";
import { Default as ContactCardStory } from "@agir/front/genericComponents/ContactCard.stories";
import TopBar from "@agir/front/allPages/TopBar";
import { decorateArgs, reorganize } from "@agir/lib/utils/storyUtils";

export default {
  component: EventPage,
  title: "Events/EventPage",
  decorators: [
    (story, { args }) => (
      <TestGlobalContextProvider
        value={{ user: args.logged ? {} : null, routes: testGlobalRoutes }}
      >
        <div style={{ paddingTop: "4.5em" }}>
          <TopBar />
          {story()}
        </div>
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
    endTime: {
      type: "string",
      control: { type: "date" },
    },
  },
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

const testGlobalRoutes = { login: "#login", join: "#signin" };

const defaultStartTime = DateTime.local().plus({ days: 2 });
const defaultEndTime = defaultStartTime.plus({ hours: 2 });

const Template = decorateArgs(
  reorganize({
    location: { name: "locationName", address: "locationAddress" },
  }),
  EventPage
);

export const Default = Template.bind({});
Default.args = {
  id: "12343432423",
  name: "Super événement",
  ...DescriptionStory.args,
  ...EventInfoStory.args,
  isOrganizer: false,
  rsvp: "CO",
  groups: [{ ...GroupCardStory.args }],
  contact: { ...ContactCardStory.args },
  startTime: defaultStartTime.toISO(),
  endTime: defaultEndTime.toISO(),
  timezone: "Europe/Paris",
  options: { price: null },
  routes: testAppRoutes,
  locationName: "Place de la République",
  locationAddress: "Place de la République\n75011 Paris",
};
