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
      url: "https://www.youtube.com/channel/UCZpyv_I2kx4FemBXYgKfomQ/",
      name: "YouTube",
    },
    {
      url: "https://twitter.com/NousSommesPour",
      name: "Twitter",
    },
    {
      url: "https://www.facebook.com/NousSommesPour",
      name: "Facebook",
    },
    {
      url: "https://www.instagram.com/noussommespour/",
      name: "Instagram",
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
  name: "Lien personnalisé",
};
