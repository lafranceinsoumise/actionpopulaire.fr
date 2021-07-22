import React from "react";

import GroupSuggestions from "./GroupSuggestions";

export default {
  component: GroupSuggestions,
  title: "Group/GroupSuggestions",
};

const Template = (args) => {
  return <GroupSuggestions {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  groups: [
    {
      id: "a",
      name: "Comités d'appui et de travail pour une Vienne Insoumise",
      iconConfiguration: { color: "#49b37d", iconName: "book" },
      url: "#group-detail",
      location: {
        city: "Poitiers",
        zip: "86000",
        coordinates: { coordinates: [-97.14704, 49.8844] },
      },
    },
    {
      id: "b",
      name: "Comités d'appui et de travail pour une Vienne Insoumise",
      iconConfiguration: { color: "#49b37d", iconName: "book" },
      url: "#group-detail",
      location: {
        city: "Poitiers",
        zip: "86000",
        coordinates: { coordinates: [-97.14704, 49.8844] },
      },
    },
    {
      id: "c",
      name: "Comités d'appui et de travail pour une Vienne Insoumise",
      iconConfiguration: { color: "#49b37d", iconName: "book" },
      url: "#group-detail",
      location: {
        city: "Poitiers",
        zip: "86000",
        coordinates: { coordinates: [-97.14704, 49.8844] },
      },
    },
  ],
};
