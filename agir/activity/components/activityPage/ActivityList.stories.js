import React from "react";

import ActivityList from "./ActivityList";
import * as RequiredActionCardStories from "./RequiredActionCard.stories";

export default {
  component: ActivityList,
  title: "Activities/ActivityList",
  argTypes: {},
};

const Template = (args) => {
  return (
    <div>
      <ActivityList {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  data: [
    {
      id: String(Date.now() + 1),
      type: "group-coorganization-accepted",
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
        fullName: "Clara Zetkin",
        email: "clara@zetkin.com",
      },
      timestamp: Date.now(),
    },
    ...Object.values(RequiredActionCardStories)
      .map(({ args }) => args)
      .filter(Boolean),
  ],
};
