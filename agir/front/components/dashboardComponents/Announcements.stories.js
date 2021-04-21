import React from "react";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import Announcements, {
  BannerAnnouncements,
  SidebarAnnouncements,
} from "./Announcements";

export default {
  component: Announcements,
  title: "Dashboard/Announcements",
};

const Template = (args) => (
  <TestGlobalContextProvider>
    {args.displayType === "sidebar" ? (
      <SidebarAnnouncements {...args} />
    ) : (
      <BannerAnnouncements {...args} />
    )}
  </TestGlobalContextProvider>
);

export const Sidebar = Template.bind({});
Sidebar.args = {
  displayType: "sidebar",
  announcements: [
    {
      id: "bcd",
      title: "Meeting numérique ce samedi !",
      content:
        "Participez en ligne au premier meeting numérique de campagne de Jean-Luc Mélenchon",
      image: {
        mobile: "https://www.fillmurray.com/160/160",
        desktop: "https://www.fillmurray.com/510/260",
      },
      link: "https://actionpopulaire.fr",
    },
    {
      id: "abc",
      title: "Meeting numérique ce samedi !",
      content:
        "Participez en ligne au premier meeting numérique de campagne de Jean-Luc Mélenchon",
      image: {
        mobile: "https://www.fillmurray.com/800/600",
        desktop: "https://www.fillmurray.com/510/260",
      },
      link: "https://actionpopulaire.fr",
    },
    {
      id: "def",
      title: "Meeting numérique ce samedi !",
      content:
        "Participez en ligne au premier meeting numérique de campagne de Jean-Luc Mélenchon",
      image: {
        mobile: "https://www.fillmurray.com/800/600",
        desktop: "https://www.fillmurray.com/510/260",
      },
      link: "https://actionpopulaire.fr",
    },
  ],
};

export const Banner__Carousel = Template.bind({});
Banner__Carousel.args = {
  ...Sidebar.args,
  displayType: "banner",
};
export const Banner__Single = Template.bind({});
Banner__Single.args = {
  ...Sidebar.args,
  announcements: Sidebar.args.announcements.slice(0, 1),
  displayType: "banner",
};
