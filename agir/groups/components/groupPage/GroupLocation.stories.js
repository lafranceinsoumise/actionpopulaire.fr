import React from "react";

import GroupLocation from "./GroupLocation";

export default {
  component: GroupLocation,
  title: "Group/GroupLocation",
};

const Template = (args) => {
  return (
    <GroupLocation
      {...args}
      location={{
        name: args.locationName,
        address1: args.locationAddress1,
        address2: args.locationAddress2,
        city: args.locationCity,
        zip: args.locationZip,
        state: args.locationState,
        country: args.locationCountry,
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
  locationName: "Le café de la gare",
  locationAddress1: "1 Place de la République",
  locationAddress2: "Au fond à gauche",
  locationCity: "Poitiers",
  locationZip: "86000",
  locationState: "Île-de-France",
  locationCountry: "France",
  latitude: -97.14704,
  longitude: 49.8844,
  iconConfiguration: { color: "#49b37d", iconName: "book" },
};
