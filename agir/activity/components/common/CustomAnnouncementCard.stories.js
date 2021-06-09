import React from "react";
import shortUUID from "short-uuid";

import { CustomAnnouncementCard } from "./CustomAnnouncementCard";

export default {
  component: CustomAnnouncementCard,
  title: "Activities/CustomAnnouncementCard",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => {
  return <CustomAnnouncementCard {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  config: {
    id: "f45b1022-939a-48c7-9977-940c0cbd69a8",
    title: "tellMore",
    link: "http://agir.local:8000/activite/f45b1022-939a-48c7-9977-940c0cbd69a8/lien/",
    content: "<p>Bienvenue !</p>",
    image: {},
    startDate: "2021-03-25T16:26:57+01:00",
    endDate: null,
    priority: 0,
    activityId: 282472,
    customDisplay: "tellMore",
    status: "I",
  },
  title: "Une annonce incroyable!",
  children: "Cette annonce est vraiment incroyable!",
  illustration: `https://robohash.org/${shortUUID.generate()}.png`,
};
