import React from "react";

import GroupBanner from "./GroupBanner";

const groupTypes = [
  "Groupe local",
  "Groupe thématique",
  "Groupe fonctionnel",
  "Groupe professionel",
  "Équipe de soutien « Nous Sommes Pour ! »",
];

export default {
  component: GroupBanner,
  title: "Group/GroupBanner",
  argTypes: {
    type: {
      defaultValue: "Groupe local",
      control: {
        type: "select",
        required: true,
        options: groupTypes,
      },
    },
  },
};

const Template = (args) => {
  return (
    <GroupBanner
      {...args}
      location={{
        city: args.city,
        zip: args.zip,
        coordinates: {
          type: "Point",
          coordinates:
            args.latitude && args.longitude
              ? [args.latitude, args.longitude]
              : null,
        },
      }}
    />
  );
};

export const Default = Template.bind({});
Default.args = {
  name: "Comités d'appui et de travail pour une Vienne Insoumise",
  type: groupTypes[0],
  city: "Poitiers",
  zip: "86000",
  latitude: -97.14704,
  longitude: 49.8844,
  iconConfiguration: { color: "#49b37d", iconName: "book" },
};
