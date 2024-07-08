import React from "react";

import GroupLinks from "./GroupLinks.js";

export default {
  component: GroupLinks,
  title: "GroupSettings/GroupLinks/LinkList",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <GroupLinks {...args} />;

export const Default = Template.bind({});
Default.args = {
  links: [
    {
      id: 1,
      label: "Présentation sur Youtube",
      url: "https://youtube.com/watch?v=ZZ5LpwO-An4",
    },
    {
      id: 2,
      label: "Groupe Facebook",
      url: "https://www.facebook.com/lafranceinsoumise/?locale=fr_FR",
    },
    { id: 3, label: "Boucle Telegram", url: "https://t.me/FranceInsoumise" },
    {
      id: 3,
      label: "Boucle départementale",
      url: "https://actionpopulaire.fr",
    },
    {
      id: 4,
      label: "Instagram",
      url: "instagram.com/franceinsoumise/",
    },
    {
      id: 5,
      label: "Blog",
      url: "https://le-blog.com",
    },
  ],
};

export const Empty = Template.bind({});
Empty.args = {
  links: [],
};
