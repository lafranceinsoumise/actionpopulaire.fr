import React from "react";

import { Default as EventCardStory } from "./EventCard.stories";

import ActivityCard from "./ActivityCard";

export default {
  component: ActivityCard,
  title: "Folder/ActivityCard",
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
