import { Default as EventCardStory } from "@agir/front/genericComponents/EventCard.stories";

import ActivityCard from "./ActivityCard";
import CONFIG from "./activity.config.json";
import { DateTime } from "luxon";
import { decorateArgs, reorganize } from "@agir/lib/utils/storyUtils";

export default {
  component: ActivityCard,
  title: "Activities/ActivityCard",
  parameters: {
    layout: "centered",
  },
  argTypes: {
    type: {
      name: "Type de carte",
      control: {
        type: "select",
        options: Object.keys(CONFIG),
      },
    },
    event: {
      control: { type: "object" },
    },
    supportGroup: {
      control: { type: "object" },
    },
  },
};

/**
 * Convertit startTime/duration fourni par les contrôles dans le format attendu
 * par le composant : startTime et endTime, au format ISO tous les deux.
 */
const convertDatetimes = ({
  event: { startTime, duration, ...event },
  ...args
}) => {
  const start = DateTime.fromMillis(startTime);
  return {
    ...args,
    event: {
      ...event,
      startTime: start.toISO(),
      endTime: start.plus({ hours: duration }).toISO(),
    },
  };
};

const Template = decorateArgs(
  convertDatetimes,
  reorganize(
    {
      "event.location": {
        name: "event.locationName",
        address: "event.locationAddress",
        shortAddress: "event.shortAddress",
      },
    },
    true
  ),
  ActivityCard
);

export const Default = Template.bind({});
Default.args = {
  id: 1,
  type: "group-coorganization-accepted",
  event: EventCardStory.args,
  supportGroup: {
    name: "Super groupe génial",
    url: "#url",
    routes: {
      manage: "#group-manage",
    },
  },
  individual: {
    displayName: "Clara",
    email: "clara@example.com",
  },
  timestamp: DateTime.local().minus({ hours: 5 }).toISO(),
  meta: {
    totalReferrals: 10,
    oldGroup: "An old group",
    transferredMemberships: 1000,
  },
  routes: {
    createEvent: "#createEvent",
    createGroup: "#createGroup",
  },
};
