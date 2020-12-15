import React from "react";

import Announcement from "./Announcement";

export default {
  component: Announcement,
  title: "Generic/Announcement",
};

const Template = (args) => {
  return (
    <div
      style={{
        maxWidth: 396,
        margin: "10px auto",
      }}
    >
      <Announcement {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  id: "123123sdqds",
  title: "Meeting numérique ce samedi !",
  content:
    "Participez en ligne au <a href='#'>premier meeting numérique de campagne de Jean-Luc Mélenchon</a>",
  image: {
    mobile: "https://www.fillmurray.com/800/600",
    desktop: "https://www.fillmurray.com/510/260",
  },
  link: "https://actionpopulaire.fr",
};
