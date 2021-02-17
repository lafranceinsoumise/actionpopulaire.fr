import React from "react";

import Activities from "@agir/activity/common/Activities";
import ActivityCard from "./ActivityCard";

export default {
  component: Activities,
  title: "Activities/ActivityList",
  argTypes: {},
};

const Template = (args) => {
  return <Activities {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  activities: [
    {
      id: 1,
      type: "event-update",
      event: {
        id: "12343432423",
        name: "Super événement",
        rsvp: "CO",
        participantCount: 6,
        duration: 1,
        illustration:
          "https://i.picsum.photos/id/523/1920/1080.jpg?hmac=sy_3fHrsxYu8cmYYWmQ2yWzPMfGNI42qloxWKF97ISk",
        location: {
          name: "Place de la République",
          address: "Place de la République\n75011 Paris",
          shortAddress: "Place de la République, 75011, Paris",
        },
        startTime: new Date().toISOString(),
        endTime: new Date().toISOString(),
        routes: {
          join: "#join",
          cancel: "#cancel",
          compteRendu: "#compteRendu",
        },
      },
      supportGroup: { name: "Super groupe génial", url: "#url" },
      individual: {
        displayName: "Clara Zetkin",
        email: "clara@zetkin.com",
      },
      timestamp: Date.now(),
    },
  ],
  CardComponent: ActivityCard,
};

export const Empty = Template.bind({});
Empty.args = {
  activities: [],
  onDismiss: () => {},
};
