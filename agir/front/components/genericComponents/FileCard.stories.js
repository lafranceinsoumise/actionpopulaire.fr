import React from "react";

import FileCard from "./FileCard";

export default {
  component: FileCard,
  title: "Generic/FileCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <FileCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  title: "Fichier super-utile",
  text: "Format PDF - 250 Kio",
  icon: "tv",
  downloadLabel: "Télécharger le fichier",
  downloadIcon: "Download",
  route: "attestationAssurance",
};
