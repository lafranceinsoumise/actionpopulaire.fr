import React from "react";

import GroupSuggestionCard from "./GroupSuggestionCard";

export default {
  component: GroupSuggestionCard,
  title: "Group/GroupSuggestionCard",
};

const Template = (args) => {
  return (
    <GroupSuggestionCard
      {...args}
      location={{
        city: args.locationCity,
        zip: args.locationZip,
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
  locationCity: "Poitiers",
  locationZip: "86000",
  latitude: -97.14704,
  longitude: 49.8844,
  iconConfiguration: { color: "#49b37d", iconName: "book" },
  url: "#group-detail",
};
