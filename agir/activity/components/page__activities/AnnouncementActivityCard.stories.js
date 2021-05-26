import React from "react";
import AnnouncementActivityCard from "./AnnouncementActivityCard";

export default {
  component: AnnouncementActivityCard,
  title: "Activities/AnnouncementActivityCard",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => <AnnouncementActivityCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  id: "4ffb6d51-df76-4621-a933-7679edfced91",
  title: "16 mai : Meeting de Jean-Luc Mélenchon",
  link: "http://agir.local:8000/activite/4ffb6d51-df76-4621-a933-7679edfced91/lien/",
  content:
    "<p>Réservez votre après-midi pour le premier meeting en plein air à la campagne #MeetingAubin</p>",
  image: {
    desktop: "https://www.fillmurray.com/255/130",
    mobile: "https://www.fillmurray.com/160/160",
    activity: "https://www.fillmurray.com/548/241",
  },
  startDate: "2021-05-17T17:33:46+02:00",
  endDate: null,
  priority: 0,
  activityId: 1341,
  customDisplay: "",
};
