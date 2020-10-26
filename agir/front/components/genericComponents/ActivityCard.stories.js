import React from "react";

import { Default as EventCardStory } from "./EventCard.stories";

import ActivityCard from "./ActivityCard";
import { eventCardIcons } from "@agir/front/genericComponents/ActivityCard";

export default {
  component: ActivityCard,
  title: "Activities/ActivityCard",
  argTypes: {
    type: {
      name: "Type de carte",
      control: {
        type: "select",
        options: Object.keys(eventCardIcons),
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
};
