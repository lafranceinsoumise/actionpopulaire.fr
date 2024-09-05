import React from "react";

import GroupLinks from "./GroupLinks";

export default {
  component: GroupLinks,
  title: "Group/GroupLinks",
};

const Template = (args) => {
  const { url, name } = args;
  const links = [
    {
      url: "https://actionpopulaire.fr/groupes/aec78081-3b87-40d5-b097-e8374eef4a89/",
      label: "Action pop",
    },
    {
      url: "https://www.youtube.com/channel/UCZpyv_I2kx4FemBXYgKfomQ/",
      label: "YouTube",
    },
    {
      url: "https://twitter.com/NousSommesPour",
      label: "Twitter",
    },
    {
      url: "https://www.facebook.com/NousSommesPour",
      label: "Facebook",
    },
    {
      url: "https://www.instagram.com/noussommespour/",
      label: "Instagram",
    },
  ];
  if (url && name) {
    links.push({
      url: url,
      name: name,
    });
  }
  return <GroupLinks links={links} />;
};

export const Default = Template.bind({});
Default.args = {
  url: "https://example.com",
  label: "Lien personnalisé",
};
