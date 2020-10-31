import React from "react";

import { Default as EventCardStory } from "@agir/front/genericComponents/EventCard.stories";

import ActivityCard from "./ActivityCard";
import { activityCardIcons } from "./ActivityCard";
import { DateTime } from "luxon";

export default {
  component: ActivityCard,
  title: "Activities/ActivityCard",
  argTypes: {
    type: {
      name: "Type de carte",
      control: {
        type: "select",
        options: Object.keys(activityCardIcons),
      },
    },
  },
};

const Template = (args) => <ActivityCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  type: "group-coorganization-accepted",
  event: EventCardStory.args,
  supportGroup: {
    name: "Super groupe génial",
    url: "#url",
  },
  individual: "Clara Zetkin",
  timestamp: DateTime.local().minus({ hours: 5 }).toISO(),
};
